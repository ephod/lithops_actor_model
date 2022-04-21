<div id="top"></div>

# Lithops and actor model

## About the project

The actor model is a math model for concurrent computations, where the 🧔 actor symbolizes the universal primitive of concurrent computation.

For this project, I will showcase four examples where Lithops (Python-based library) can work using the actor model. Lithops has three execution modes:

1. Localhost
2. Serverless
3. Standalone

This project is a technical demonstration of what you can achieve with serverless functions and how to adapt our code using the actor model.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#uninstall">Uninstall</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#mnist">MNIST</a></li>
      </ul>
    </li>
    <li>
      <a href="#built-with">Built With</a>
      <ul>
        <li><a href="#serverless-mode">Serverless mode</a></li>
        <li><a href="#compute-backend">Compute backend</a></li>
        <li><a href="#storage-backend">Storage backend</a></li>
      </ul>
    </li>
    <li>
      <a href="#redis">Redis</a>
      <ul>
        <li><a href="#troubleshooting-redis">Troubleshooting Redis</a></li>
      </ul>
    </li>
    <li>
      <a href="#terraform-for-provisioning-redis-(optional)">Terraform for provisioning Redis (optional)</a>
      <ul>
        <li><a href="#cheat-sheet-for-terraform-cli">Cheat sheet for Terraform CLI</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

### Actor model implementation

The code related to the actor model implementation within Lithops was based on this source code: https://github.com/danielBCN/lithops-actors

The author is Daniel Barcelona: https://github.com/danielBCN

Code: `./actor_model/director.py`

<p align="right">(<a href="#top">back to top</a>)</p>

## Getting started

### Prerequisites

Creating a virtual environment, activating it, and installing the necessary packages.

```shell
# Create Python's virtual environment
python3 -m venv .venv
# Activate Python's virtual environment
source .venv/bin/activate
# Upgrade pip to the latest version
python -m pip install --upgrade pip
```

<p align="right">(<a href="#top">back to top</a>)</p>

### Installation

```shell
# Production
python -m pip install -r requirements.txt
# Development
# python -m pip install -r requirements-dev.txt
```

<p align="right">(<a href="#top">back to top</a>)</p>

### Uninstall

Exit Python's virtual environment.

```shell
# Exit Python's virtual environment
deactivate
# Remove Python's virtual environment folder
rm -rf .venv/
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

1. Counter: `python actor_model/counter.py`
2. Ping pong: `python actor_model/mnist.py`
3. Bank account: `python actor_model/mnist.py`
4. MNIST: `python actor_model/mnist.py`

View logs after each run.

```shell
lithops logs poll
```

<p align="right">(<a href="#top">back to top</a>)</p>

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

<p align="right">(<a href="#top">back to top</a>)</p>

## Built with

https://github.com/lithops-cloud/lithops

Configuration file for serverless mode:

```shell
# Configuration file example for Lithops serverless mode
cp .lithops_config.example .lithops_config
```

<p align="right">(<a href="#top">back to top</a>)</p>

### Serverless mode

Lithops configuration: [Serverless mode](https://github.com/lithops-cloud/lithops/blob/master/config/README.md#compute-and-storage-backends)

### Compute backend

Lithops configuration: [AWS Lambda](https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/aws_lambda.md)

### Storage backend

1. The first iteration will use [Amazon S3](https://aws.amazon.com/s3/) (Amazon Simple Storage Service) as a cloud object storage.

   Lithops configuration: [AWS S3](https://github.com/lithops-cloud/lithops/blob/master/docs/source/storage_config/aws_s3.md)

2. The subsequent runs will use [Redis](https://redis.io/), due to Redis Stack nature of offering different data structures.
   
   Lithops configuration: [Redis](https://github.com/lithops-cloud/lithops/blob/master/docs/source/storage_config/redis.md)

<p align="right">(<a href="#top">back to top</a>)</p>

## Redis

In my particular case, I'm using DigitalOcean's Redis service as it is relatively easy to spin up a new instance and destroy it afterwards.

The RESP.app documentation gives a wonderful insight of the different solutions provided by different cloud providers:
https://docs.resp.app/en/latest/quick-start/

<p align="right">(<a href="#top">back to top</a>)</p>

### Troubleshooting Redis

* The main reason against using **AWS ElastiCache** (Amazon's managed Redis), is that you can only access it within your VPC (Virtual Private Cloud). Instructions are provided to circumvent these restrictions.
* **Azure Cache for Redis** can be accessed from outside of Azure's VPC but Terraform's integration with Azure is not quite stable for me.
  * The port number is usually `6380` instead of the default `6379` port.
* **DigitalOcean** uses a different port such as `25061`.

Redis out of the box supports 16 databases, 0 is the default one.

To delete the current database run the following command.

```shell
flushdb
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Terraform for provisioning Redis (optional)

Terraform by HashiCorp is used for IaC (Infrastructure as Code). I've included an example for DigitalOcean managed Redis instance.

This Redis instance has 🔒 encryption at rest and in transit: https://docs.digitalocean.com/products/databases/redis/how-to/secure/

1. Install Terraform CLI: https://learn.hashicorp.com/tutorials/terraform/install-cli
2. Install Terraform providers.
    ```shell
    # Install providers
    terraform init
    ```
3. Create a variable definition file for DigitalOcean's personal access token.
    ```shell
    # File with DigitalOcean personal access token ignored by GIT due to .gitignore
    cat << EOF >> digital-ocean.tfvars
    digital_ocean_token = ""
    EOF
    ```
4. Use the variable definition file to spin up the Redis instance.
    ```shell
    # Use variable definitions and create an output file with the changes needed for Terraform apply
    terraform plan --var-file=digital-ocean.tfvars --input=false --out lithops.tfplan
    # DigitalOcean will now spin a managed Redis instance
    terraform apply "lithops.tfplan"
    ```
5. Retrieve Redis configuration.
    ```shell
    # After several minutes retrieve host, port, and password
    terraform show --json
    ```
6. Destroy the Redis instance to keep costs low.
    ```shell
    # Destroy managed Redis instance
    terraform destroy --var-file=digital-ocean.tfvars
    ```

<p align="right">(<a href="#top">back to top</a>)</p>

### Cheat sheet for Terraform CLI

Documentation: https://www.terraform.io/cli/commands

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

<p align="right">(<a href="#top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

## Contact

Michael A. Johnson Lucas - mjohnson(at)uoc.edu

Project Link: [https://github.com/ephod/lithops_actor_model](https://github.com/ephod/lithops_actor_model)

<p align="right">(<a href="#top">back to top</a>)</p>
