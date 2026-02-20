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
                echo "Cleaning up past deployments (if any)..."
                // Run the cleanup script now that gns3-server and venv are ready
                sh "${VENV_PATH}/bin/python3 cleanup_gns3.py probeweave_test"
            }
        }

        stage('Register GNS3 Templates') {
            steps {
                echo "Registering Alpine QEMU image and template..."
                sh "${VENV_PATH}/bin/python3 register_templates.py"
            }
        }

        stage('Infrastructure Provisioning') {
            steps {
                echo "Provisioning new GNS3 project and topology..."
                sh "${VENV_PATH}/bin/python3 provision_gns3.py infrastructure.yml"
                // Run tests for this stage
                sh "${VENV_PATH}/bin/pytest test_infrastructure.py::test_gns3_server_reachable"
                sh "${VENV_PATH}/bin/pytest test_infrastructure.py::test_project_provisioned"
            }
        }

        stage('Bootstrap Nodes') {
            steps {
                echo "Bootstrapping nodes via Serial Console (Injecting Network/SSH)..."
                sh "chmod +x bootstrap_nodes.py"
                sh "./bootstrap_nodes.py"
                // Verify nodes are started and SSH is up
                sh "${VENV_PATH}/bin/pytest test_infrastructure.py::test_nodes_running"
                sh "${VENV_PATH}/bin/pytest test_infrastructure.py::test_ssh_connectivity"
            }
        }

        stage('System Crawl (ProbeWeave)') {
            steps {
                echo "Running ProbeWeave Ansible Crawler..."
                sh "${VENV_PATH}/bin/ansible-playbook -i gns3_inventory.py site.yml"
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
