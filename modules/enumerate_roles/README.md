# AWS IAM Roles and Policies Enumerator

This script enumerates IAM roles and their associated policies across multiple AWS profiles. It retrieves account names, validates credentials, and generates a report in CSV format.

## Features

- Enumerates IAM roles and their associated policies (both inline and managed).
- Supports multiple AWS profiles from a configuration file.
- Validates AWS credentials before processing.
- Provides real-time feedback using a spinner for a better user experience.
- Generates a CSV report with role details.

## Prerequisites

- Python 3.x
- AWS CLI configured with multiple profiles
- Required Python dependencies:
  - `boto3`
  - `configparser`
  - `halo`

## Installation

1. Install dependencies:

   ```sh
   pip install boto3 halo
```

2. Ensure your AWS profiles are correctly configured in ~/.aws/config and credentials in ~/.aws/credentials.

3. Create a separate profile configuration file (/home/user1/.aws/.python-profiles.conf) and define profiles in the format:

```
[testProfile]
profile_list = profile1 profile2 profile3
```

# Usage

##  Running the script for all configured profiles:
```
python3 enumerate_roles.py
```

# Output

The script saves results in /tmp/YYYY-MM-DD.IamRolesAndTheirPolicies.csv

# Example Output

```
Casting 'Enumerate IAM Roles and Policies' spell on account: MyAWSAccount...
✅ Spell 'Enumerate IAM Roles and Policies' successfully cast on account: MyAWSAccount
The report has been saved to: /tmp/YYYY-MM-DD.IamRolesAndTheirPolicies.csv
```

