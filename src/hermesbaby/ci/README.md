<!---
################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################
-->

# CI Build Agent Documentation (Ubuntu 24.04)

Docker image for building and publishing documentation using the docs-as-code toolchain with hermesbaby.

## Overview

This Docker image provides a complete environment for:

- Building documentation from source code using hermesbaby
- Packaging the generated HTML documentation
- Publishing to the corporate documentation portal

## Image Contents

- **Base**: Ubuntu 24.04 build agent
- **Documentation Tools**: hermesbaby and dependencies
- **Build Script**: Embedded `/usr/local/bin/run.sh` for automated builds
- **SSH Server**: For VS Code Remote-SSH development access

## Jenkins Integration

### 1. Docker Image Configuration

Use the image in your Jenkins pipeline:

```groovy
// In your Jenkinsfile or pipeline configuration
def dockerImage = "packages.my-company.com:443/docker/hermesbaby-ci:latest"

node {
    docker.image(dockerImage).inside() {
        // Your build steps here
    }
}
```

### 2. Required Environment Variables

The build process requires these environment variables to be configured:

#### From Jenkins Vault (Credentials)

```bash
SECRET_HERMES_API_TOKEN  # API token for docs.your-company.com
```

#### From Jenkins Job Configuration

```bash
branch          # Git branch name (e.g., 'develop', 'main', 'feature/xyz')
componentName   # Component name for documentation (e.g., 'BiomechDevDocs')
gitProject      # Git project identifier (e.g., 'BIOM')
```

### 3. Jenkins Pipeline Example

```groovy
pipeline {
    agent {
        docker {
            image 'packages.my-company.com:443/docker/hermesbaby-ci:latest'
        }
    }

    environment {
        // Set from Jenkins credentials
        SECRET_DOCS_YOUR_COMPANY_COM_API_TOKEN = credentials('docs-your-company-com-api-token')

        // Set from job parameters or SCM info
        branch = "${env.BRANCH_NAME}"
        componentName = "YourComponentName"
        gitProject = "YOUR_PROJECT"
    }

    stages {
        stage('Build and Publish Documentation') {
            steps {
                sh 'run.sh'
            }
        }
    }
}
```

### 4. Legacy Jenkins Job Configuration

For traditional Jenkins jobs (not pipeline):

1. **Build Environment**:
   - Check "Build inside a Docker container"
   - Docker Image: `packages.my-company.com:443/docker/hermesbaby-ci:latest`

2. **Environment Variables**:
   - Add environment variables in job configuration:
     - `branch` = `${GIT_BRANCH}`
     - `componentName` = `YourComponentName`
     - `gitProject` = `YOUR_PROJECT`

3. **Credentials**:
   - Bind credential `SECRET_HERMES_API_TOKEN` from Jenkins vault

4. **Build Steps**:
   - Add "Execute shell" step: `run.sh`

## Build Process

The embedded `run.sh` script performs these steps:

1. **Git Checkout**: Switches to the specified branch (if provided)
2. **Documentation Build**: Generates HTML using `hb html`
3. **Packaging**: Creates `html.tar.gz` archive
4. **Publishing**: Uploads to `https://docs.your-company.com/projects/$gitProject/$componentName/$branch`

## Configuration Files

The build process looks for `.hermesbaby` configuration file in the project root. If not found, it defaults to:

```bash
CONFIG_BUILD__DIRS__BUILD=out/docs
```

## Development Usage

### Local Development with VS Code Remote-SSH

The image includes SSH server for development:

1. Run container with SSH port exposed:

   ```bash
   docker run -d -p 2222:22 \
     -v /path/to/your/project:/workspace \
     packages.my-company.com:443/docker/hermesbaby-ci:latest
   ```

2. Connect via VS Code Remote-SSH to `localhost:2222`

### Manual Build Testing

Run a one-off build:

```bash
docker run --rm \
  -v /path/to/your/docs:/workspace \
  -w /workspace \
  -e branch=develop \
  -e componentName=TestDocs \
  -e gitProject=TEST \
  -e SECRET_HERMES_API_TOKEN=your_token \
  packages.my-company.com:443/docker/hermesbaby-ci:latest \
  run.sh
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**:
   - The script will fail immediately with `set -u` if required variables are not set
   - Check Jenkins job configuration and credentials binding

2. **Permission Issues**:
   - Ensure Jenkins has access to the Docker registry
   - Verify API token has correct permissions for docs.your-company.com

3. **Build Failures**:
   - Check hermesbaby configuration (`.hermesbaby` file)
   - Verify source documentation files are present
   - Check build logs for specific hermesbaby errors

### Debug Mode

For debugging, you can override the entry point:

```bash
docker run -it --rm \
  -v /path/to/your/docs:/workspace \
  -w /workspace \
  --entrypoint /bin/bash \
  packages.my-company.com:443/docker/hermesbaby-ci:latest
```

## Building the Image

To build this image locally:

```bash
docker build -t hermesbaby-ci .
```
