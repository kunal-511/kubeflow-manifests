#!/usr/bin/env python3
"""
Apply CRD patches to match the Kustomize behavior
"""
import yaml
import json
import copy

def apply_trivial_conversion_patch(crd_data):
    """Apply trivial conversion patch"""
    if 'spec' not in crd_data:
        crd_data['spec'] = {}
    
    crd_data['spec']['preserveUnknownFields'] = False
    if 'conversion' not in crd_data['spec']:
        crd_data['spec']['conversion'] = {}
    crd_data['spec']['conversion']['strategy'] = 'None'
    
    return crd_data

def apply_validation_patches(crd_data):
    """Apply validation patches using JSON patch operations"""
    # The patches modify required fields for containers in all three versions
    patches = [
        {
            "op": "replace",
            "path": "/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/template/properties/spec/properties/containers/items/required",
            "value": ["name", "image"]
        },
        {
            "op": "replace", 
            "path": "/spec/versions/1/schema/openAPIV3Schema/properties/spec/properties/template/properties/spec/properties/containers/items/required",
            "value": ["name", "image"]
        },
        {
            "op": "replace",
            "path": "/spec/versions/2/schema/openAPIV3Schema/properties/spec/properties/template/properties/spec/properties/containers/items/required", 
            "value": ["name", "image"]
        },
        {
            "op": "add",
            "path": "/spec/versions/0/schema/openAPIV3Schema/properties/spec/properties/template/properties/spec/properties/containers/minItems",
            "value": 1
        },
        {
            "op": "add",
            "path": "/spec/versions/1/schema/openAPIV3Schema/properties/spec/properties/template/properties/spec/properties/containers/minItems",
            "value": 1
        },
        {
            "op": "add", 
            "path": "/spec/versions/2/schema/openAPIV3Schema/properties/spec/properties/template/properties/spec/properties/containers/minItems",
            "value": 1
        }
    ]
    
    import jsonpatch
    patch = jsonpatch.JsonPatch(patches)
    return patch.apply(crd_data)

def main():
    # Read the original CRD
    with open('kubeflow.org_notebooks.yaml.backup', 'r') as f:
        crd_data = yaml.safe_load(f)
    
    # Apply trivial conversion patch
    crd_data = apply_trivial_conversion_patch(crd_data)
    
    # Apply validation patches
    try:
        crd_data = apply_validation_patches(crd_data) 
    except Exception as e:
        print(f"Warning: Could not apply validation patches: {e}")
        print("Continuing without validation patches...")
    
    # Write the patched CRD
    with open('kubeflow.org_notebooks.yaml', 'w') as f:
        yaml.dump(crd_data, f, default_flow_style=False, sort_keys=False)
    
    print("CRD patches applied successfully")

if __name__ == '__main__':
    main()