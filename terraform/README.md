Worked and tested for dev purposes yet.

# Create S3 bucket and DynamoDB for Terraform backend
One time task only. May be needed for preparing new AWS account only.

    export AWS_ACCESS_KEY_ID=<your_key>
    export AWS_SECRET_ACCESS_KEY=<your_secret_key>
    export AWS_DEFAULT_REGION=eu-central-1
    cd terraform/remote_back/
    terraform init
    terraform apply --var-file=backend.tfvars

Confirm and type "yes", wait and you should see something like this:

    Apply complete! Resources: 5 added, 0 changed, 0 destroyed.


# Install modules and plug-ins for Terrafrom 
terraform init -backend-config=remote_back/backend.conf

# Create, switch and list Terrafrom workspaces

S3 backend support multiple named workspaces, allowing multiple states to be associated with a single configuration. The configuration still has only one backend, but multiple distinct instances of that configuration to be deployed without configuring a new backend or changing authentication credentials.
So we need at least 2 workspaces: dev and prod

## Create a new workspace
    terraform workspace new dev 
## Change to the selected workspace
    terraform workspace select dev 
## Lst out all workspaces
    terraform workspace list 

# Deploy

## Preview only
terraform plan --var-file=environments/dev.tfvars

## Deploy resources
terraform apply --var-file=environments/dev.tfvars

# Destroy resources
terraform destroy --var-file=environments/dev.tfvars