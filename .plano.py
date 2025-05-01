#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from plano import *
from plano.github import *

@command
def build(no_cache=False):
    """
    Build the images
    """

    no_cache_arg = "--no-cache" if no_cache else ""

    with working_dir("frontend"):
        run(f"plano build {no_cache_arg}")

    with working_dir("backend"):
        run(f"plano build {no_cache_arg}")

@command
def test():
    """
    Test the images
    """

    backend_port = get_random_port()
    frontend_port = get_random_port()

    with start(f"podman run --net host quay.io/skupper/hello-world-backend --host localhost --port {backend_port}"):
        with start(f"podman run --net host quay.io/skupper/hello-world-frontend --host localhost --port {frontend_port}"
                   f" --backend http://localhost:{backend_port}"):
            await_port(backend_port)
            await_port(frontend_port)

            http_get(f"http://localhost:{backend_port}/api/health")
            http_get(f"http://localhost:{backend_port}/api/hello")

            http_get(f"http://localhost:{frontend_port}/")
            http_post_json(f"http://localhost:{frontend_port}/api/hello", {"name": "Obtuse Ocelot", "text": "Bon jour"})

            data = http_get_json(f"http://localhost:{frontend_port}/api/data")

            assert data[0]["request"]["name"] == "Obtuse Ocelot", data
            assert data[0]["response"]["text"].startswith("Hi, Obtuse Ocelot"), data
            assert data[0]["error"] is None, data

    backend_port = get_random_port()
    frontend_port = get_random_port()

    with start(f"podman run --net host quay.io/skupper/hello-world-frontend --host localhost --port {frontend_port}"
               f" --backend http://localhost:{backend_port}"):
        await_port(frontend_port)

        with expect_error():
            result = http_get(f"http://localhost:{backend_port}/api/health")

@command
def run():
    """
    Run the images
    """

    backend_port = 8081
    frontend_port = 8080

    with start(f"podman run --net host quay.io/skupper/hello-world-backend --host localhost --port {backend_port}"):
        with start(f"podman run --net host quay.io/skupper/hello-world-frontend --host localhost --port {frontend_port}"
                   f" --backend http://localhost:{backend_port}"):
            await_port(backend_port)
            await_port(frontend_port)

            sleep(86400)

@command
def update_plano():
    """
    Update the embedded Plano repo
    """
    update_external_from_github("external/plano", "ssorj", "plano")
