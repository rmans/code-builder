// bad code with lint errors
export const hello = (name: string) => {
  var result = "hi"
  if (name) {
    result = result + ", " + name
  }
  return result
}

// unused variable
const unused = "this is not used"

// missing return type
function badFunction(x: number) {
  return x * 2
}

// inconsistent naming
const Bad_Variable_Name = "bad"
const anotherBadVariableName = "also bad"

// no error handling
export const divide = (a: number, b: number) => a / b
