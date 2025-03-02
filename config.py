# config.py

# Huawei Cloud 
CREDENTIALS = {
    "ak": "BYJ15CSXRF44ONZK1HAG",
    "sk": "u4DdWpG7pU59DCjOHCsOvzOI9HQcq22OqnV1HbUG",
    "region": "ap-southeast-2" 
}

# Auto Scaling Group 
ASG_CONFIG = {
    "group_id": "bdf403d1-3e76-4cb5-8fb2-e95a81aa2839", 
    "min_size": 1,
    "desired_capacity": 2,
    "max_size": 3
}

# Instance Config
INSTANCE_CONFIG = {
    "flavor_id": "s6.small.1",
    "key_name": "KeyPair-best",
    "security_group_id": "f6c94959-7c58-4e68-ab08-cd6d395a3846",  
    "vpc_id": "1c4c83c4-43b5-462d-aaa1-26480643d6fa",  
    "subnet_id": "b2a7c353-f15a-4189-a25a-e42ff50013b3"  
}

# Terraform Config
TERRAFORM_CONFIG = {
    "image_id": "aa4ad3d8-8241-4e5f-b479-e158f8722ab2",  
    "template_version": "v3"
}