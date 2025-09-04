import { hello } from '../src/hello';
describe('hello', () => {
    it('returns "hi" with no args', () => {
        expect(hello()).toBe('hi');
    });
    it('greets by name when provided', () => {
        expect(hello('Alice')).toBe('hi, Alice');
    });
});
//# sourceMappingURL=hello.test.js.map