"""Notify platform tests for mobile_app."""
from datetime import datetime, timedelta

import pytest

from homeassistant.components.mobile_app.const import DOMAIN
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry


@pytest.fixture
async def setup_push_receiver(hass, aioclient_mock, hass_admin_user):
    """Fixture that sets up a mocked push receiver."""
    push_url = "https://mobile-push.home-assistant.dev/push"

    now = datetime.now() + timedelta(hours=24)
    iso_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    aioclient_mock.post(
        push_url,
        json={
            "rateLimits": {
                "attempts": 1,
                "successful": 1,
                "errors": 0,
                "total": 1,
                "maximum": 150,
                "remaining": 149,
                "resetsAt": iso_time,
            }
        },
    )

    entry = MockConfigEntry(
        data={
            "app_data": {"push_token": "PUSH_TOKEN", "push_url": push_url},
            "app_id": "io.homeassistant.mobile_app",
            "app_name": "mobile_app tests",
            "app_version": "1.0",
            "device_id": "4d5e6f",
            "device_name": "Test",
            "manufacturer": "Safegate Pro",
            "model": "mobile_app",
            "os_name": "Linux",
            "os_version": "5.0.6",
            "secret": "123abc",
            "supports_encryption": False,
            "user_id": hass_admin_user.id,
            "webhook_id": "mock-webhook_id",
        },
        domain=DOMAIN,
        source="registration",
        title="mobile_app test entry",
        version=1,
    )
    entry.add_to_hass(hass)

    await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
    await hass.async_block_till_done()

    loaded_late_entry = MockConfigEntry(
        data={
            "app_data": {"push_token": "PUSH_TOKEN2", "push_url": f"{push_url}2"},
            "app_id": "io.homeassistant.mobile_app",
            "app_name": "mobile_app tests",
            "app_version": "1.0",
            "device_id": "4d5e6f2",
            "device_name": "Loaded Late",
            "manufacturer": "Safegate Pro",
            "model": "mobile_app",
            "os_name": "Linux",
            "os_version": "5.0.6",
            "secret": "123abc2",
            "supports_encryption": False,
            "user_id": "1a2b3c2",
            "webhook_id": "webhook_id_2",
        },
        domain=DOMAIN,
        source="registration",
        title="mobile_app 2 test entry",
        version=1,
    )
    loaded_late_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(loaded_late_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service("notify", "mobile_app_loaded_late")

    assert await hass.config_entries.async_remove(loaded_late_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service("notify", "mobile_app_test")
    assert not hass.services.has_service("notify", "mobile_app_loaded_late")

    loaded_late_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(loaded_late_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service("notify", "mobile_app_test")
    assert hass.services.has_service("notify", "mobile_app_loaded_late")


async def test_notify_works(hass, aioclient_mock, setup_push_receiver):
    """Test notify works."""
    assert hass.services.has_service("notify", "mobile_app_test") is True
    assert await hass.services.async_call(
        "notify", "mobile_app_test", {"message": "Hello world"}, blocking=True
    )

    assert len(aioclient_mock.mock_calls) == 1
    call = aioclient_mock.mock_calls

    call_json = call[0][2]

    assert call_json["push_token"] == "PUSH_TOKEN"
    assert call_json["message"] == "Hello world"
    assert call_json["registration_info"]["app_id"] == "io.homeassistant.mobile_app"
    assert call_json["registration_info"]["app_version"] == "1.0"


async def test_notify_ws_works(
    hass, aioclient_mock, setup_push_receiver, hass_ws_client
):
    """Test notify works."""
    client = await hass_ws_client(hass)

    await client.send_json(
        {
            "id": 5,
            "type": "mobile_app/push_notification_channel",
            "webhook_id": "mock-webhook_id",
        }
    )

    sub_result = await client.receive_json()
    assert sub_result["success"]

    # Subscribe twice, it should forward all messages to 2nd subscription
    await client.send_json(
        {
            "id": 6,
            "type": "mobile_app/push_notification_channel",
            "webhook_id": "mock-webhook_id",
        }
    )

    sub_result = await client.receive_json()
    assert sub_result["success"]

    assert await hass.services.async_call(
        "notify", "mobile_app_test", {"message": "Hello world"}, blocking=True
    )

    assert len(aioclient_mock.mock_calls) == 0

    msg_result = await client.receive_json()
    assert msg_result["event"] == {"message": "Hello world"}
    assert msg_result["id"] == 6  # This is the new subscription

    # Unsubscribe, now it should go over http
    await client.send_json(
        {
            "id": 7,
            "type": "unsubscribe_events",
            "subscription": 6,
        }
    )
    sub_result = await client.receive_json()
    assert sub_result["success"]

    assert await hass.services.async_call(
        "notify", "mobile_app_test", {"message": "Hello world 2"}, blocking=True
    )

    assert len(aioclient_mock.mock_calls) == 1

    # Test non-existing webhook ID
    await client.send_json(
        {
            "id": 8,
            "type": "mobile_app/push_notification_channel",
            "webhook_id": "non-existing",
        }
    )
    sub_result = await client.receive_json()
    assert not sub_result["success"]
    assert sub_result["error"] == {
        "code": "not_found",
        "message": "Webhook ID not found",
    }

    # Test webhook ID linked to other user
    await client.send_json(
        {
            "id": 9,
            "type": "mobile_app/push_notification_channel",
            "webhook_id": "webhook_id_2",
        }
    )
    sub_result = await client.receive_json()
    assert not sub_result["success"]
    assert sub_result["error"] == {
        "code": "unauthorized",
        "message": "User not linked to this webhook ID",
    }
