// ---------------------------------------------------------
// Tests for /emails
// ---------------------------------------------------------

pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
})

pm.test('Content-Type is present', function () {
    pm.response.to.have.header('Content-Type');
})

pm.test("Valid token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.eql(false);
});

pm.test("Schema is valid", function () {
  var schema = {
    type: "object",
    properties: {
      emails: {
        type: "array",
        items: {
          type: "object",
          properties: {
            bodyPreview: { type: "string" },
            id: { type: "string" },
            sender: {
              type: "object",
              properties: {
                address: { type: "string" },
                name: { type: "string" }
              },
              required: ["address", "name"]
            },
            subject: { type: "string" },
            time: { type: "string" }
          },
          required: ["bodyPreview", "id", "sender", "subject", "time"]
        },
      },
      error: { type: "boolean" },
      totalEmails: { type: "number" }
    },
    required: ["emails", "error", "totalEmails"],
  };

  var response = pm.response.json();
  pm.expect(tv4.validate(response, schema)).to.be.true;
});

pm.test("The emails array length must be greater than zero", function () {
    const responseData = pm.response.json();
    const emails = responseData.emails;
   
    pm.expect(emails.length).to.be.greaterThan(0, "Emails array should not be empty");

    emails.forEach((email)=>{
      pm.expect(email.bodyPreview).to.be.a('string', "Email bodyPreview should be a string");
      pm.expect(email.id).to.be.a('string', "Email id should be a string");

      const sender = email.sender;
      pm.expect(sender).to.be.an('object').that.has.property('address').that.is.a('string', "Sender address should be a string");
      pm.expect(sender).to.have.property('name').that.is.a('string', "Sender name should be a string");

      pm.expect(email.subject).to.be.a('string', "Email subject should be a string");
      pm.expect(email.time).to.be.a('string', "Email time should be a string");
    });
});

// ---------------------------------------------------------
// Tests for /emails/{id}
// ---------------------------------------------------------

pm.test('Response status code is 200', function () {
    pm.expect(pm.response.code).to.equal(200);
})

pm.test('Bcc and cc are arrays', function () {
    const responseData = pm.response.json();
    pm.expect(responseData.email.bcc).to.be.an('array');
    pm.expect(responseData.email.cc).to.be.an('array');
})

pm.test("Sender's address and name are non-empty strings", function () {
  const responseData = pm.response.json();
  
  pm.expect(responseData.email.sender.address).to.be.a('string').and.to.have.lengthOf.at.least(1, "Address should not be empty");
  pm.expect(responseData.email.sender.name).to.be.a('string').and.to.have.lengthOf.at.least(1, "Name should not be empty");
});

pm.test('Error field is present and has a boolean value', function () {
    const responseData = pm.response.json();
    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData.error).to.exist.and.to.be.a('boolean');
})

// ---------------------------------------------------------
// Tests for /getByCategory
// ---------------------------------------------------------

pm.test("Response status code is 200", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Content-Type is application/json", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

pm.test("Emails array is present in the response", function () {
    const responseData = pm.response.json();

    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData.emails).to.exist.and.to.be.an('array');
});

pm.test("Error field is present and has a boolean value", function () {
    const responseData = pm.response.json();
    
    pm.expect(responseData).to.have.property('error').that.is.a('boolean');
});

pm.test("TotalEmails field is present and has a numeric value", function () {
    const responseData = pm.response.json();

    pm.expect(responseData).to.be.an('object');
    pm.expect(responseData.totalEmails).to.exist;
    pm.expect(responseData.totalEmails).to.be.a('number');
});

// ---------------------------------------------------------
// Tests for /changeCategory
// ---------------------------------------------------------

pm.test("Response status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has the required field 'error'", function () {
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
