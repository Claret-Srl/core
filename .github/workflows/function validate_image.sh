bash <(curl https://getvcn.codenotary.com -L)

export DOCKER_CLI_EXPERIMENTAL=enabled

function create_manifest() {
    local docker_reg=${1}
    local tag_l=${2}
    local tag_r=${3}

    docker manifest create "${docker_reg}/home-assistant:${tag_l}" \
        "${docker_reg}/amd64-homeassistant:${tag_r}" \
        "${docker_reg}/i386-homeassistant:${tag_r}" \
        "${docker_reg}/armhf-homeassistant:${tag_r}" \
        "${docker_reg}/armv7-homeassistant:${tag_r}" \
        "${docker_reg}/aarch64-homeassistant:${tag_r}"

    docker manifest annotate "${docker_reg}/home-assistant:${tag_l}" \
        "${docker_reg}/amd64-homeassistant:${tag_r}" \
        --os linux --arch amd64

    docker manifest annotate "${docker_reg}/home-assistant:${tag_l}" \
        "${docker_reg}/i386-homeassistant:${tag_r}" \
        --os linux --arch 386

    docker manifest annotate "${docker_reg}/home-assistant:${tag_l}" \
        "${docker_reg}/armhf-homeassistant:${tag_r}" \
        --os linux --arch arm --variant=v6

    docker manifest annotate "${docker_reg}/home-assistant:${tag_l}" \
        "${docker_reg}/armv7-homeassistant:${tag_r}" \
        --os linux --arch arm --variant=v7

    docker manifest annotate "${docker_reg}/home-assistant:${tag_l}" \
        "${docker_reg}/aarch64-homeassistant:${tag_r}" \
        --os linux --arch arm64 --variant=v8

    docker manifest push --purge "${docker_reg}/home-assistant:${tag_l}"
}

function validate_image() {
    local image=${1}

    if [[ "$VCN_SIGNER" =~ ^0x ]]; then
        local vcn_cli=("--signerID")
    else
        local vcn_cli=("--org")
    fi

    state="$(vcn authenticate "$vcn_cli" "$VCN_SIGNER" --output json docker://"${image}" | jq '.verification.status // 2')"

    if [[ "${state}" != "0" ]]; then
        echo "Invalid signature!"
        exit 1
    fi
}

for docker_reg in "drypatrick" "ghcr.io/drypatrick"; do
    for arch in "amd64" "i386" "armhf" "armv7" "aarch64"; do
        docker pull "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
        validate_image "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
    done

for docker_reg in "drypatrick" "ghcr.io/drypatrick"; do
    for arch in "amd64" "i386" "armhf" "armv7" "aarch64"; do
        docker pull "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
        validate_image "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
    done

    # Create version tag
    create_manifest "${docker_reg}" "${{ needs.init.outputs.version }}" "${{ needs.init.outputs.version }}"

    # Create general tags
    if [[ "${{ needs.init.outputs.version }}" =~ d ]]; then
        local versions = ("dev")
    elif [[ "${{ needs.init.outputs.version }}" =~ b ]]; then
        local versions = ("beta" "rc")
    else
        local versions = ("stable" "latest" "beta" "rc")
    fi

    for version in "${versions[@]}"; do
        create_manifest "${docker_reg}" "${version}" "${{ needs.init.outputs.version }}"
    done
done
          
          
          
          
          
          
# function validate_image() {
#     local image=${1}

#     if [[ "$VCN_ORG" =~ ^0x ]]; then
#         vcn_cli="--signerID"
#     else
#         vcn_cli="--org" 
#     fi

#     state="$(vcn authenticate ${vcn_cli} ${VCN_ORG} --output json docker://${image} | jq '.verification.status // 2')"

#     if [[ "${state}" != "0" ]]; then
#         echo "Invalid signature!"
#         exit 1
#     fi
# }
          
# for docker_reg in "drypatrick" "ghcr.io/drypatrick"; do
#     for arch in "amd64" "i386" "armhf" "armv7" "aarch64"; do
#         docker pull "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
#         validate_image "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
#     done

#     # Create version tag
#         create_manifest "${docker_reg}" "${{ needs.init.outputs.version }}" "${{ needs.init.outputs.version }}"

#         # Create general tags
#         if [[ "${{ needs.init.outputs.version }}" =~ d ]]; then
#             local versions = ("dev")
#         elif [[ "${{ needs.init.outputs.version }}" =~ b ]]; then
#             local versions = ("beta" "rc")
#         else
#             local versions = ("stable" "latest" "beta" "rc")
#         fi

#         for version in "${versions[@]}"; do
#             create_manifest "${docker_reg}" "${version}" "${{ needs.init.outputs.version }}"
#         done
# done
