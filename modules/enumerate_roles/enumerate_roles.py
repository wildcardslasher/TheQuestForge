#!/usr/bin/env python3

import boto3
import configparser
import datetime
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
from botocore.config import Config
from halo import Halo

# AWS configuration with retry policy
config = Config(
    retries=dict(
        max_attempts=10
    )
)

# File paths and setup
config_file = '/home/user1/.aws/.python-profiles.conf'
today = datetime.date.today().strftime("%F")
report_file = f"/tmp/{today}.IamRolesAndTheirPolicies.csv"

# Initialize report file with header
with open(report_file, "w") as file:
    file.write("ROLE_NAME;ROLE_PATH;ROLE_ID;ROLE_ARN;POLICY_NAMES;POLICY_ARNS;POLICY_TYPE;ACCOUNT_NAME;ACCOUNT_NR\n")

def summon_profiles(config_file):
    """Spell to summon (read) AWS profiles from the configuration file."""
    config = configparser.ConfigParser()
    config.read(config_file)
    profile_list = config.get('testProfile', 'profile_list').split(' ') # choose your profile/profiles here
    return profile_list

def validate_credentials(profile_name):
    """Validate AWS credentials for the given profile."""
    try:
        session = boto3.Session(profile_name=profile_name)
        sts = session.client('sts', config=config)
        sts.get_caller_identity()
        return True
    except NoCredentialsError:
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidClientTokenId' or error_code == 'ExpiredToken':
            return False
        raise  # Re-raise unexpected ClientErrors
    except EndpointConnectionError:
        print("ERROR: Could not connect to AWS endpoint. Please check your internet connection.")
        return False

def get_account_name(profile_name):
    """Retrieve the account name for the specified AWS profile."""
    try:
        session = boto3.Session(profile_name=profile_name)
        iam = session.client('iam', config=config)
        sts = session.client('sts', config=config)
        aws_account = sts.get_caller_identity().get('Account')
        account_alias = iam.list_account_aliases()
        account_name = account_alias['AccountAliases'][0] if account_alias['AccountAliases'] else aws_account
        return account_name
    except (NoCredentialsError, ClientError) as e:
        print(f"ERROR: Failed to retrieve account identity for profile '{profile_name}'.")
        return None

def enumerate_roles_and_policies(spell_title, profile_name):
    profile_name = profile_name.replace('"', '')
    """Spell to enumerate IAM roles and their policies for a given AWS profile."""
    session = boto3.Session(profile_name=profile_name)
    iam = session.client('iam', config=config)
    sts = session.client('sts', config=config)

    # Initialize spinner at the start
    spinner = None

    try:
        account_name = get_account_name(profile_name)
        if not account_name:
            print(f"ERROR: Skipping profile '{profile_name}' due to account retrieval failure.")
            return

        # Spinner indicating the start of the spell
        spinner = Halo(text=f"Casting '{spell_title}' spell on account: {account_name}", spinner="dots", color="cyan")
        spinner.start()

        paginator = iam.get_paginator('list_roles')
        page_iterator = paginator.paginate()

        for page in page_iterator:
            for role in page['Roles']:
                role_name = role['RoleName']
                role_arn = role['Arn']
                role_id = role['RoleId']
                role_path = role['Path']
                account_nr = role_arn.split('::')[1].split(':')[0]

                # Process inline policies
                inline_policies = iam.list_role_policies(RoleName=role_name)['PolicyNames']
                policy_names = inline_policies or "NO-INLINE-POLICIES"
                policy_arns = "N/A" if not inline_policies else []
                policy_type = "inline" if inline_policies else "N/A"

                # Write inline policies to the report
                write_line = f"{role_name};{role_path};{role_id};{role_arn};{policy_names};{policy_arns};{policy_type};{account_name};{account_nr}"
                with open(report_file, "a") as file:
                    print(write_line, file=file)

                # Process managed policies
                managed_policies = iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
                policy_names = [policy['PolicyName'] for policy in managed_policies] or "NO-MANAGED-POLICIES"
                policy_arns = [policy['PolicyArn'] for policy in managed_policies] or "N/A"
                policy_type = "managed" if managed_policies else "N/A"

                write_line = f"{role_name};{role_path};{role_id};{role_arn};{policy_names};{policy_arns};{policy_type};{account_name};{account_nr}"
                with open(report_file, "a") as file:
                    print(write_line, file=file)

        if spinner:
            spinner.succeed(f"Spell '{spell_title}' successfully cast on account: {account_name}")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        # Handle InvalidClientTokenId error specifically
        if error_code == 'InvalidClientTokenId':
            print(f"ERROR - Invalid or expired credentials for profile '{profile_name}'. Please check your AWS credentials.")
            print(f"Skipping {profile_name}")
        else:
            print(f"ClientError encountered for profile '{profile_name}': {e}")
        
        spinner.fail(f"Failed to cast spell '{spell_title}' on account: {profile_name}")
    
    except Exception as e:
        # Catch any other general exceptions
        print(f"An unexpected error occurred for profile '{profile_name}': {e}")
        spinner.fail(f"Failed to cast spell '{spell_title}' on account: {profile_name}")


def main_loop(spell_title, profiles=None):
    # If a single profile is passed as a string, wrap it in a list
    if isinstance(profiles, str):
        profiles = [profiles]
    elif profiles is None:
        profiles = summon_profiles(config_file)  # Load profiles if not provided
    
    for profile in profiles:
        profile_name = profile.replace('"', '').strip()
        spinner = Halo(text=f"Validating credentials for profile: {profile_name}", spinner="dots", color="cyan")
        spinner.start()
        if validate_credentials(profile_name):
            spinner.succeed(f"Credentials validated for profile: {profile_name}")
            enumerate_roles_and_policies(spell_title, profile_name)
        else:
            spinner.fail(f"Skipping '{profile_name}' due to invalid or expired credentials")

    # Notify user where the CSV report is saved
    print(f"\nThe report has been saved to: {report_file}")

# Main execution part to make the script runnable independently
if __name__ == "__main__":
    # Default spell title and load profiles if run independently
    default_spell_title = "Enumerate IAM Roles and Policies"
    main_loop(default_spell_title)