const fetch = require("node-fetch");

module.exports = function (RED) {
    function CustomNode(config) {
        RED.nodes.createNode(this, config);
        {% for param_name, param in node.parameters.items() %}
        this['{{ param_name }}'] = config['{{ param_name }}'];
        {% if param.typed_input %}
        this['{{ param_name + TYPED_INPUT_TYPE_SUFFIX}}'] = config['{{ param_name + TYPED_INPUT_TYPE_SUFFIX}}'];
        {% endif %}
        {% endfor %}
        var node = this;
        node.paramConfig = {{ node.to_dict() | json | safe}};
        // node.on('input', function (msg) {
        //     msg.payload = msg.payload.toLowerCase();
        //     node.send(msg);
        // });

        node.on('input', function (msg) {
            console.log(node.paramConfig);
            // parse params
            var urlParams = {};
            var routeParams = {};
            var bodyParams = {};
            node.paramConfig.parameter_list.forEach((paramName) => {
                const paramConfig = node.paramConfig.parameters_config[paramName];
                var value = node[paramName];
                if (value !== '' || paramConfig.required) {
                    if (paramConfig.typed_input) {
                        value = RED.util.evaluateNodeProperty(value, node[paramName + '{{ TYPED_INPUT_TYPE_SUFFIX }}'], node, msg);
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
            if (Object.keys(bodyParams).length !== 0) {
                fetchOptions.body = JSON.stringify(bodyParams);
            }

            // TODO: authentification


            // Perform the API call using the Fetch API
            fetch(apiUrl, fetchOptions)
                .then(response => {
                    msg.response = {
                        status: response.status,
                        headers: response.headers
                    };
                    return response.json();
                })
                .then(data => {
                    // Save the JSON response in the msg object
                    msg.payload = data;
                    node.send(msg);
                })
                .catch(error => {
                    node.error('Error making API call: ' + error.message);
                });
        });

    }

    RED.nodes.registerType('{{ node.name }}', CustomNode);
}
