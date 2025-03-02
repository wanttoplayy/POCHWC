# asg_updater.py

import subprocess
import time
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkas.v1.region.as_region import AsRegion
from huaweicloudsdkas.v1 import *
from config import CREDENTIALS, ASG_CONFIG, INSTANCE_CONFIG, TERRAFORM_CONFIG

class ASGUpdater:
    def __init__(self):
        self.credentials = BasicCredentials(
            ak=CREDENTIALS["ak"],
            sk=CREDENTIALS["sk"]
        )
        self.client = AsClient.new_builder() \
            .with_credentials(self.credentials) \
            .with_region(AsRegion.value_of(CREDENTIALS["region"])) \
            .build()

    def get_instance_list(self, group_id):
        try:
            request = ListScalingInstancesRequest()
            request.scaling_group_id = group_id
            response = self.client.list_scaling_instances(request)
            return response.scaling_group_instances
        except Exception as e:
            print(f"Error getting instance list: {e}")
            return []

    def force_instance_refresh(self, group_id):
        try:
            print("\n=== Starting Instance Refresh ===")
            
            # Verify ASG exists
            print(f"\nVerifying Auto Scaling Group {group_id}...")
            try:
                describe_request = ShowScalingGroupRequest()
                describe_request.scaling_group_id = group_id
                self.client.show_scaling_group(describe_request)
            except Exception as e:
                print(f"Error: Auto Scaling Group {group_id} not found or not accessible")
                raise

            # Get current instances
            print("\nChecking current instances...")
            current_instances = self.get_instance_list(group_id)
            if current_instances:
                print(f"Found {len(current_instances)} current instances:")
                for instance in current_instances:
                    print(f"- Instance ID: {instance.instance_id}")
            else:
                print("No current instances found")

            # Set min instances to 0
            print("\nModifying group capacity...")
            modify_request = UpdateScalingGroupRequest()
            modify_request.scaling_group_id = group_id
            modify_request.body = UpdateScalingGroupOption(
                min_instance_number=0,
                desire_instance_number=0
            )
            self.client.update_scaling_group(modify_request)
            print("Group capacity modified")

            # Remove existing instances
            if current_instances:
                print("\nRemoving existing instances...")
                remove_request = BatchRemoveScalingInstancesRequest()
                remove_request.scaling_group_id = group_id
                remove_request.body = BatchRemoveInstancesOption(
                    instances_id=[inst.instance_id for inst in current_instances],
                    action="REMOVE",
                    instance_delete="yes"
                )
                self.client.batch_remove_scaling_instances(remove_request)
                print("Removal request sent successfully")

            # Reset group capacity
            print("\nResetting group capacity...")
            reset_request = UpdateScalingGroupRequest()
            reset_request.scaling_group_id = group_id
            reset_request.body = UpdateScalingGroupOption(
                min_instance_number=ASG_CONFIG["min_size"],
                desire_instance_number=ASG_CONFIG["desired_capacity"],
                delete_publicip=True,
                delete_volume=True
            )
            self.client.update_scaling_group(reset_request)
            print("Group capacity reset")
            
            # Wait and check new instances
            print("Waiting for new instances to be created...")
            time.sleep(60)
            
            new_instances = self.get_instance_list(group_id)
            if new_instances:
                print(f"\nNew instances created ({len(new_instances)}):")
                for instance in new_instances:
                    print(f"- Instance ID: {instance.instance_id}")
            else:
                print("\nNo new instances found yet")
            
            print("\n=== Instance Refresh Completed ===")
            
        except Exception as e:
            print(f"\nError during instance refresh: {e}")
            raise

    def create_terraform_vars(self, new_image_id, template_version):
        with open("terraform.tfvars", "w") as f:
            f.write(f'''
                template_version = "{template_version}"
                image_id = "{new_image_id}"
                flavor_id = "{INSTANCE_CONFIG['flavor_id']}"
                key_name = "{INSTANCE_CONFIG['key_name']}"
                desired_capacity = {ASG_CONFIG['desired_capacity']}
                min_size = {ASG_CONFIG['min_size']}
                max_size = {ASG_CONFIG['max_size']}
                security_group_id = "{INSTANCE_CONFIG['security_group_id']}"
                vpc_id = "{INSTANCE_CONFIG['vpc_id']}"
                subnet_id = "{INSTANCE_CONFIG['subnet_id']}"
            ''')

    def apply_new_configuration(self, new_image_id=None, template_version=None):
        try:
            print("\n=== Starting Configuration Update ===")
            
            # Use default values if not provided
            new_image_id = new_image_id or TERRAFORM_CONFIG["image_id"]
            template_version = template_version or TERRAFORM_CONFIG["template_version"]
            
            print(f"\nUpdating configuration with:")
            print(f"- New Image ID: {new_image_id}")
            print(f"- Template Version: {template_version}")
            
            # Create terraform vars file
            print("\nCreating terraform.tfvars file...")
            self.create_terraform_vars(new_image_id, template_version)

            print("\nInitializing Terraform...")
            subprocess.run(["terraform", "init"], check=True)
            
            print("\nApplying new configuration...")
            subprocess.run(["terraform", "apply", "-auto-approve"], check=True)
            
            print("\nStarting instance refresh process...")
            self.force_instance_refresh(ASG_CONFIG["group_id"])
            
            time.sleep(60)
            
            print("\n=== Update Process Completed Successfully! ===")
            
        except subprocess.CalledProcessError as e:
            print(f"\nError during terraform execution: {e}")
        except Exception as e:
            print(f"\nError during update: {e}")
            raise