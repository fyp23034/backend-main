// for GET requests
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// for POST requests
pm.test("Successful POST request", function () {
    pm.expect(pm.response.code).to.be.oneOf([201, 202]);
});

// for '/email'
pm.test("Correct schema for /email", function () {

})

// for routes which involve an access token
pm.test("Valid token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.eql(False);
});