const fetch = require("node-fetch");

module.exports = function (RED) {
    function CustomNode(config) {
        RED.nodes.createNode(this, config);
        var node = this;
        node.nodeConfig = config;
        node.paramConfig = {{ node.to_dict() | json | safe}};
        // node.on('input', function (msg) {
        //     msg.payload = msg.payload.toLowerCase();
        //     node.send(msg);
        // });

        node.on('input', function (msg) {
            // console.log(node.nodeConfig);
            // parse params
            var urlParams = {};
            var routeParams = {};
            var bodyParams = {};
            node.paramConfig.parameter_list.forEach((paramName) => {
                const paramConfig = node.paramConfig.parameters_config[paramName];
                var value = node.nodeConfig[paramName];
                if (value !== '' || paramConfig.required) {
                    if (paramConfig.typed_input && !paramConfig.options) {
                        value = RED.util.evaluateNodeProperty(value, node.nodeConfig[paramName + '{{ TYPED_INPUT_TYPE_SUFFIX }}'], node, msg);
                    } else if (paramConfig.typed_input && paramConfig.options && paramConfig.multiple_select) {
                        value = value.split(',').map(part => part.trim());
                    }
                    if (paramConfig.url_param) {
                        urlParams[paramName] = value;
                    } else if (paramConfig.route_param) {
                        routeParams[paramName] = value;
                    } else {
                        bodyParams[paramName] = value;
                    }
                }
            });

            // construct url
            var apiUrl = node.paramConfig.url;
            for (const [k, v] of Object.entries(routeParams)) {
                apiUrl = apiUrl.replace(`%%${k}%%`, v);
            }

            // URL params
            if (Object.keys(urlParams).length !== 0) {
                // Convert the dictionary to a URL-encoded string
                const urlencodedString = Object.entries(urlParams)
                    .map(([key, value]) => encodeURIComponent(key) + '=' + encodeURIComponent(value))
                    .join('&');

                // Append the URL-encoded string to the apiUrl
                apiUrl += '?' + urlencodedString;
            }


            // fetch options
            var fetchOptions = {
                method: node.paramConfig.method,
                headers: {
                    "Content-Type": "application/json"
                }
            };

            // body
            {% if node.has_body_params() %}
            var jsonBody = node.nodeConfig.json_body ? RED.util.evaluateNodeProperty(node.nodeConfig.json_body, node.nodeConfig['json_body{{ TYPED_INPUT_TYPE_SUFFIX }}'], node, msg) : null;
            if (jsonBody) {
                fetchOptions.body = JSON.stringify(jsonBody);
            } else {
                fetchOptions.body = JSON.stringify(bodyParams);
            }
            {% endif %}

            {% if node.parent.authentication %}
            // authentification
            fetchOptions.headers['{{ node.parent.authentication_header }}'] = RED.util.evaluateNodeProperty(node.credentials.authentication, node.nodeConfig['authentication{{ TYPED_INPUT_TYPE_SUFFIX }}'], node, msg);

            {% endif %}


            // Perform the API call using the Fetch API
            fetch(apiUrl, fetchOptions)
                .then(response => {
                    msg.response = {
                        status: response.status,
                        headers: response.headers
                    };

                    // Check if the response is JSON
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json();
                    } else {
                        // If not JSON, return the response text directly
                        return response.text();

                    }
                })
                .then(data => {
                    if (typeof data === 'string') {
                        node.error('Response is not in JSON format: ' + data);
                    } else {
                        msg.payload = data;
                        node.send(msg);
                    }


                })
                .catch(error => {
                    node.error('Error making API call: ' + error.message);
                });
        });

    }

    var registerTypeOptions = {};
    {% if node.parent.authentication %}
    registerTypeOptions.credentials = {authentication: {type: "text"}};
    {% endif %}
    RED.nodes.registerType('{{ node.name }}', CustomNode, registerTypeOptions);
}
