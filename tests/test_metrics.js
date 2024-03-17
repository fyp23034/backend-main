// ---------------------------------------------------------
// Tests for /recordTime
// ---------------------------------------------------------

pm.test("Response status code is 200", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response body contains the 'error' field", function () {
    const responseData = pm.response.json();
    
    pm.expect(responseData).to.have.property('error');
});

pm.test("Error field is a boolean value", function () {
  const responseData = pm.response.json();
  
  pm.expect(responseData.error).to.be.a('boolean');
});

pm.test("Verify Content-Type header is application/json", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});


// ---------------------------------------------------------
// Tests for /recordClick
// ---------------------------------------------------------


pm.test("Response status code is 200", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response has the required fields", function () {
    const responseData = pm.response.json();

    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData.error).to.exist;
});

pm.test("Error field is present in the response", function () {
    const responseData = pm.response.json();
    pm.expect(responseData.error).to.exist;
});

pm.test("Error field has a boolean value", function () {
    const responseData = pm.response.json();
    
    pm.expect(responseData.error).to.be.a('boolean');
});
