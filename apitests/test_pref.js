// ---------------------------------------------------------
// Tests for /getPreferences
// ---------------------------------------------------------

pm.test("Response status code is 200", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response has the required fields", function () {
    const responseData = pm.response.json();
    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData).to.have.property('error');
    pm.expect(responseData).to.have.property('prefList');
    pm.expect(responseData).to.have.property('whitelist');
});

pm.test("Error field is boolean", function () {
    const responseData = pm.response.json();
    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData.error).to.be.a('boolean');
});

pm.test("PrefList and whitelist are arrays", function () {
    const responseData = pm.response.json();
    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData.prefList).to.be.an('array');
    pm.expect(responseData.whitelist).to.be.an('array');
});

pm.test("PrefList and Whitelist arrays should not be empty", function () {
    const responseData = pm.response.json();
    
    pm.expect(responseData.prefList).to.be.an('array').and.to.have.lengthOf.at.least(1, "PrefList should not be empty");
    pm.expect(responseData.whitelist).to.be.an('array').and.to.have.lengthOf.at.least(1, "Whitelist should not be empty");
});

// ---------------------------------------------------------
// Tests for /setPreferences
// ---------------------------------------------------------

pm.test("Response status code is 200", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response has the required Content-Type header", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

pm.test("Error field is present in the response", function () {
  const responseData = pm.response.json();
  pm.expect(responseData.error).to.exist;
});

pm.test("Error field is a boolean value", function () {
    const responseData = pm.response.json();
    
    pm.expect(responseData.error).to.be.a('boolean');
});