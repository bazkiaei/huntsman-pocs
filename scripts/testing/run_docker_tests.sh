#!/usr/bin/env bash
# This code is presumed to be run from inside a docker container
set -e

HUNTSMAN_COVDIR="${HUNTSMAN_COVDIR:-${PANLOG}/huntsman-coverage}"
COVERAGE_REPORT_FILE="${HUNTSMAN_COVDIR}/coverage.xml"
PANOPTES_CONFIG_HOST="${PANOPTES_CONFIG_HOST:-localhost}"
PANOPTES_CONFIG_PORT="${PANOPTES_CONFIG_PORT:-8765}"
PANOPTES_CONFIG_FILE="${HUNTSMAN_POCS}/tests/testing.yaml"

export COVERAGE_PROCESS_START="${HUNTSMAN_POCS}/setup.cfg"
coverage erase

# Start the config server
echo "Starting config server in background"
echo "PANOPTES_CONFIG_FILE=${PANOPTES_CONFIG_FILE}"
echo "PANOPTES_CONFIG_HOST=${PANOPTES_CONFIG_HOST}"
echo "PANOPTES_CONFIG_PORT=${PANOPTES_CONFIG_PORT}"
panoptes-config-server --host "${PANOPTES_CONFIG_HOST}" --port "${PANOPTES_CONFIG_PORT}" run --no-load-local --no-save-local --config-file ${PANOPTES_CONFIG_FILE} &
echo "Checking to make sure panoptes-config-server is running"
/usr/local/bin/wait-for-it.sh --timeout=30 --strict "${PANOPTES_CONFIG_HOST}:${PANOPTES_CONFIG_PORT}" -- echo "Config-server up."

# Start the pyro name server
PYRO_NS_HOST="$(panoptes-config-server get pyro.nameserver.host)"
PYRO_NS_PORT="$(panoptes-config-server get pyro.nameserver.port)"
echo "Starting the Pyro nameserver on ${PYRO_NS_HOST}:${PYRO_NS_PORT}"
huntsman-pyro --verbose --host "${PYRO_NS_HOST}" --port "${PYRO_NS_PORT}" nameserver --auto-clean 300 &

# Start a pyro camera service
# TODO: Move inside conftest
echo "Creating testing Pyro CameraService"
huntsman-pyro --verbose --host 0.0.0.0 service --service-name dslr.00 --service-class huntsman.pocs.camera.pyro.service.CameraService &

# Run the tests
echo "Starting testing"
coverage run "$(command -v pytest)"

# TODO shutdown pyro service?

echo "Stopping config server"
panoptes-config-server --verbose --host "${PANOPTES_CONFIG_HOST}" --port "${PANOPTES_CONFIG_PORT}" stop

echo "Combining coverage for ${COVERAGE_REPORT_FILE}"
coverage combine

echo "Making XML coverage report at ${COVERAGE_REPORT_FILE}"
coverage xml -o "${COVERAGE_REPORT_FILE}"
coverage report --show-missing

exit 0
