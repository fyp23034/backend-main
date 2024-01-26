pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Correct schema", function () {

})

pm.test("Valid token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.eql(False);
});