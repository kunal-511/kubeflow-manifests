#!/bin/bash
set -euxo pipefail

NAMESPACES=("istio-system" "auth" "cert-manager" "oauth2-proxy" "kubeflow")

for NAMESPACE in "${NAMESPACES[@]}"; do
    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        if [ -f "./experimental/security/PSS/static/baseline/patches/${NAMESPACE}-labels.yaml" ]; then
            echo "Patching the PSS-baseline labels for namespace $NAMESPACE..."
            PATCH_OUTPUT=$(kubectl patch namespace $NAMESPACE --patch-file ./experimental/security/PSS/static/baseline/patches/${NAMESPACE}-labels.yaml 2>&1)
            echo "$PATCH_OUTPUT"
            
            if echo "$PATCH_OUTPUT" | grep -q "violate the new PodSecurity"; then
                echo "CRITICAL: PSS baseline violations detected in namespace $NAMESPACE"
                HAS_VIOLATIONS=true
            fi
        fi
    fi
done

FAILING_PODS=$(kubectl get pods --all-namespaces --field-selector=status.phase=Failed -o json | jq -r '.items[] | select(.metadata.namespace as $ns | ["istio-system", "auth", "cert-manager", "oauth2-proxy", "kubeflow"] | index($ns) != null) | .metadata.namespace + "/" + .metadata.name')

if [ -n "$FAILING_PODS" ]; then
    echo "$FAILING_PODS"
    exit 1
fi

if [ "${HAS_VIOLATIONS:-false}" = true ]; then
    echo "CRITICAL: PSS baseline violations detected in one or more namespaces"
    exit 1
fi
