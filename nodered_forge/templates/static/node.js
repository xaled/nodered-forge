const fetch = require("node-fetch");

module.exports = function (RED) {
    function CustomNode(config) {
        RED.nodes.createNode(this, config);
        var node = this;
        // node.on('input', function (msg) {
        //     msg.payload = msg.payload.toLowerCase();
        //     node.send(msg);
        // });

        node.on('input', function (msg) {
            // Construct the API call URL with parameters
            // var apiUrl = node.url + '?param1=' + node.param1 + '&param2=' + node.param2;
            var apiUrl = '{{ node.url }}';

            // Perform the API call using the Fetch API
            fetch(apiUrl)
                .then(response => response.json())
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
