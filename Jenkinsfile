pipeline {
    agent any

    environment {
        GNS3_USER = "admin"
        GNS3_PASS = "3aujKGulW9vlHztjkvHujipVu2id6p0x8cSfIAVboXGPuO1DtOuBX2fwd7yAeTSp"
        VENV_PATH = ".venv"
    }

    stages {
        stage('Bootstrap Slave Environment (System)') {
            steps {
                echo "Installing GNS3, QEMU, and dependencies on AlmaLinux 9 slave..."
                // Install Ansible on the host if not already there
                sh "python3 -m pip install --user ansible-core"
                // This playbook installs: GNS3, QEMU, ubridge, vpcs, python libs, etc.
                sh "ansible-playbook bootstrap_slave.yml"
                // Prepare the Python environment for our custom scripts
                sh "python3 -m venv ${VENV_PATH}"
                sh "${VENV_PATH}/bin/pip install -r setup/requirements.txt gns3fy pytest requests PyYAML 'pydantic<1.9' ansible-core"
            }
        }

        stage('Pre-Deployment Cleanup') {
            steps {
                echo "Cleaning up past deployments..."
                sh "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src && \${VENV_PATH}/bin/python3 -m probeweave.cleanup"
            }
        }

        stage('Register GNS3 Templates') {
            steps {
                echo "Registering Alpine QEMU image..."
                sh "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src && \${VENV_PATH}/bin/python3 -m probeweave.templates"
            }
        }

        stage('Infrastructure Provisioning') {
            steps {
                echo "Provisioning new GNS3 project..."
                sh "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src && \${VENV_PATH}/bin/python3 -m probeweave.provisioner"
            }
        }

        stage('Bootstrap Nodes') {
            steps {
                echo "Bootstrapping nodes..."
                sh "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src && \${VENV_PATH}/bin/python3 -m probeweave.bootstrapper"
            }
        }

        stage('System Crawl (ProbeWeave)') {
            steps {
                echo "Running Crawler..."
                sh "export PYTHONPATH=\$PYTHONPATH:\$(pwd)/src && \${VENV_PATH}/bin/ansible-playbook -i src/probeweave/inventory.py site.yml"
            }
        }

        stage('Test & Audit') {
            steps {
                sh "tox"
            }
        }

        stage('Analysis & Reporting') {
            steps {
                echo "Analyzing crawled data..."
                sh "${VENV_PATH}/bin/python3 analyze_results.py"
                // If using Jenkins Warnings Next Gen plugin, you can publish the MD here
            }
        }
    }

    post {
        always {
            echo "Gathering artifacts..."
            archiveArtifacts artifacts: 'output/*.json, probeweave_report.md', allowEmptyArchive: true
        }
        success {
            echo "ProbeWeave Run Successful."
        }
        failure {
            echo "ProbeWeave Run Failed. Check logs and GNS3 server status."
        }
    }
}
