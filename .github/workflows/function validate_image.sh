function validate_image() {
local image=${1}

if [[ "$VCN_ORG" =~ ^0x ]]; then
    vcn_cli="--signerID"
else
    vcn_cli="--org" 
fi

state="$(vcn authenticate ${vcn_cli} ${VCN_ORG} --output json docker://${image} | jq '.verification.status // 2')"

if [[ "${state}" != "0" ]]; then
    echo "Invalid signature!"
    exit 1
fi

}
          
for docker_reg in "drypatrick" "ghcr.io/drypatrick"; do
    for arch in "amd64" "i386" "armhf" "armv7" "aarch64"; do
        docker pull "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"
        validate_image "${docker_reg}/${arch}-homeassistant:${{ needs.init.outputs.version }}"

    # Create version tag
        create_manifest "${docker_reg}" "${{ needs.init.outputs.version }}" "${{ needs.init.outputs.version }}"

        # Create general tags
        if [[ "${{ needs.init.outputs.version }}" =~ d ]]; then
            versions = ("dev")
        elif [[ "${{ needs.init.outputs.version }}" =~ b ]]; then
            versions = ("beta" "rc")
        else
            versions = ("stable" "latest" "beta" "rc")
        fi
        for version in "${versions[@]}"; do
            create_manifest "${docker_reg}" $version "${{ needs.init.outputs.version }}"
        done
    done
done
                  local trust=0x0893a6151eccc2be56274ea043f47cb412b2a7be
                  local vcn_cli=()
                  
                  if [[ "${trust}" =~ ^0x ]]; then
                    vcn_cli+=("--signerID" "${trust}")
                  else
                    vcn_cli+=("--org" "${trust}")
                  fi

                  echo "${vcn_cli[@]}"
                  echo "vcn authenticate "${vcn_cli[@]}" --output json docker://${image}"
                  
                  # state="$(vcn authenticate "${vcn_cli[@]}" --output json docker://"${image}" | jq '.verification.status // 2')"
                  # state="$(vcn authenticate --signerID "$VCN_ORG" --output json docker://"${image}" | jq '.verification.status // 2')"
                  # state="$(vcn authenticate --signerID 0x0893a6151eccc2be56274ea043f47cb412b2a7be --output json docker://"${image}" | jq '.verification.status // 2')"
                 