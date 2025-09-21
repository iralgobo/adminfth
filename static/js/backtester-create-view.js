document.getElementById("id_strategy").addEventListener("change", function () {
    const strategy = this.value;
    fetch(getStrategySchemaUrl(strategy))
        .then(res => res.json())
        .then(schema => {
            reactJsonForm.createForm({
                containerId: 'id_parametros_jsonform',
                dataInputId: 'id_parametros',
                schema: schema
            }).render();
            
        });
});