# Lithops and actor model

The actor model is a math model for concurrent computations, where the 🧔 actor symbolizes the universal primitive of concurrent computation.

## Actor model

The code related to the actor model implementation within Lithops was based on this source code: https://github.com/danielBCN/lithops-actors

The author is Daniel Barcelona: https://github.com/danielBCN

`./actor_model/director.py`

## Installation

Creating a virtual environment, activating it, and installing the necessary packages.

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Production
python -m pip install -r requirements.txt
# Development
# python -m pip install -r requirements-dev.txt
```

## Running examples

```shell
lithops logs poll
```

### MNIST

The datasets belong to:

* Yann LeCun, Courant Institute, NYU
* Corinna Cortes, Google Labs, New York
* Christopher J.C. Burges, Microsoft Research, Redmond

http://yann.lecun.com/exdb/mnist/

The files have been decompressed and stored within `./datasets/`:

* Test set images: `t10k-images-idx3-ubyte`
* Test set labels: `t10k-labels-idx1-ubyte`
* Training set images: `train-images-idx3-ubyte`
* Training set labels: `train-images-idx1-ubyte`

The source code for MNIST with [NumPy](https://numpy.org/) has been adapted from this source: https://github.com/karynaur/mnist-from-numpy/blob/main/mnist.py

The author is Aditya Srinivas Menon: https://github.com/karynaur

```shell
python actor_model/mnist.py
```

## Uninstall

Exit Python's virtual environment.

```shell
# Exit Python's virtual environment
deactivate
# Remove Python's virtual environment folder
rm -rf .venv/
```

## 🪴 Lithops cloud

https://github.com/lithops-cloud/lithops

Configuration file for serverless mode:

```shell
# Configuration file example for Lithops serverless mode
cp .lithops_config.example .lithops_config
```

### ⚡ Serverless mode

Lithops configuration: [Serverless mode](https://github.com/lithops-cloud/lithops/blob/master/config/README.md#compute-and-storage-backends)

#### 🖥️ Compute backend

Lithops configuration: [AWS Lambda](https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/aws_lambda.md)

#### 🪣 Storage backend

1. The first iteration will use [Amazon S3](https://aws.amazon.com/s3/) (Amazon Simple Storage Service) as a cloud object storage.

   Lithops configuration: [AWS S3](https://github.com/lithops-cloud/lithops/blob/master/docs/source/storage_config/aws_s3.md)

2. The subsequent runs will use [Redis](https://redis.io/), due to Redis Stack nature of offering different data structures.
   
   Lithops configuration: [Redis](https://github.com/lithops-cloud/lithops/blob/master/docs/source/storage_config/redis.md)

In my particular case, I'm using DigitalOcean's Redis service as it is relatively easy to spin up a new instance and destroy it afterwards.

The RESP.app documentation gives a wonderful insight of the different solutions provided by different cloud providers:
https://docs.resp.app/en/latest/quick-start/

⚠️ Troubleshooting Redis:

* The main reason against using AWS ElastiCache (Amazon's managed Redis), is that you can only access it within your VPC (Virtual Private Cloud). Instructions are provided to circumvent these restrictions.
* Azure Cache for Redis can be accessed from outside of Azure's VPC but Terraform's integration with Azure is not quite stable for me.
  * The port number is usually 6380 instead of the default 6379 port.
* DigitalOcean uses a different port such as 25061.

```shell
# Redis out of the box supports 16 databases, 0 is the default one.
# Delete the current database
flushdb
```

## Terraform (for demo purposes)

Terraform by HashiCorp is used for IaC (Infrastructure as Code). I've included an example for DigitalOcean managed Redis instance.

This Redis instance has 🔒 encryption at rest and in transit: https://docs.digitalocean.com/products/databases/redis/how-to/secure/

Installation: https://learn.hashicorp.com/tutorials/terraform/install-cli

Commands: https://www.terraform.io/cli/commands

```shell
# Install providers
terraform init
# Format code
terraform fmt .
# Validate Terraform code
terraform validate
# Dry run
terraform plan
# Install
terraform apply
# Uninstall
terraform destroy
# View configuration and piping results to jq (Command-line JSON processor) https://github.com/stedolan/jq
terraform show --json | jq .
```

⚠️ Create a variable definition file for DigitalOcean's personal access token.

```shell
# File with DigitalOcean personal access token ignored by GIT due to .gitignore
cat << EOF >> digital-ocean.tfvars
digital_ocean_token = ""
EOF
```

Use the variable definition file to spin up the Redis instance.

```shell
# Use variable definitions and create an output file with the changes needed for Terraform apply
terraform plan --var-file=digital-ocean.tfvars --input=false --out lithops.tfplan
# DigitalOcean will now spin a managed Redis instance
terraform apply "lithops.tfplan"
```

```shell
# After several minutes retrieve host, port, and password
terraform show --json
# Destroy managed Redis instance
terraform destroy --var-file=digital-ocean.tfvars
```
