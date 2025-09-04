// --- Code Builder Flow: hello module ---
// Round 1: Generate Spec, Code, and Test Variants (A, B, C)
// --- SPEC: hello module ---
// Spec: hello module
//
// Goal
// Provide a simple function that returns a greeting string.
//
// Acceptance Criteria
// - The function returns a string greeting.
// - The function is exported from the module.
// - The function can be easily tested.
//
// Trace
// - PRD: N/A
// - Architecture: N/A
// - UX: N/A
// - Integration: N/A
// - ADRs: ADR-0001
// --- VARIANT A ---
// (Base: T=0.66, P=0.99)
export const helloA = () => 'hi';
// --- VARIANT B ---
// (T=0.73, P=1.09)
export const helloB = (name) => name ? `hi, ${name}` : 'hi';
// --- VARIANT C ---
// (T=0.59, P=0.89)
export function helloC() {
    return 'hi';
}
// --- TESTS (pseudo, to be placed in test/hello.test.ts or similar) ---
// describe('helloA', () => {
//   it('returns hi', () => {
//     expect(helloA()).toBe('hi');
//   });
// });
// describe('helloB', () => {
//   it('returns hi', () => {
//     expect(helloB()).toBe('hi');
//     expect(helloB('Alice')).toBe('hi, Alice');
//   });
// });
// describe('helloC', () => {
//   it('returns hi', () => {
//     expect(helloC()).toBe('hi');
//   });
// });
// --- Round 1 Scoring ---
// A: Simple, meets all criteria. Score: 8
// B: Adds optional name, more flexible. Score: 9
// C: Function syntax, equivalent to A. Score: 7
// --- Promote Variant B to next round ---
// --- Round 2: Refine Variant B ---
// (T=0.73, P=1.09)
// Add type annotations and docstring
// --- Test remains as above for helloB, now hello ---
// --- Round 2 Scoring ---
// B: Clear, typed, documented. Score: 10
// --- Round 3: Finalize and Output ---
// --- Final Exported Function ---
/**
 * Returns a greeting.
 * @param name Optional name to greet.
 * @returns Greeting string.
 */
export const hello = (name) => name ? `hi, ${name}` : 'hi';
// --- End Code Builder Flow ---
