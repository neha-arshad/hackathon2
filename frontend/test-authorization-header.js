/**
 * Quick test to verify Authorization header is set correctly
 * Run this in browser console after logging in
 */

// Simulate the cleanToken function
function cleanToken(token) {
  if (!token) return null;
  let cleaned = token.trim();
  while (/^Bearer\s+/i.test(cleaned)) {
    cleaned = cleaned.replace(/^Bearer\s+/i, '');
  }
  return cleaned.trim();
}

// Test cases
console.log('=== Authorization Header Test ===\n');

// Test 1: Clean token (no Bearer prefix)
const token1 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature';
const cleaned1 = cleanToken(token1);
const header1 = `Bearer ${cleaned1}`;
console.log('Test 1: Clean token');
console.log('Input:', token1.substring(0, 20) + '...');
console.log('Header:', header1.substring(0, 30) + '...');
console.log('Correct:', header1.match(/^Bearer [^B]/) !== null);
console.log();

// Test 2: Token with "Bearer " prefix (from old login)
const token2 = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature';
const cleaned2 = cleanToken(token2);
const header2 = `Bearer ${cleaned2}`;
console.log('Test 2: Token with "Bearer " prefix');
console.log('Input:', token2.substring(0, 30) + '...');
console.log('Cleaned:', cleaned2.substring(0, 20) + '...');
console.log('Header:', header2.substring(0, 30) + '...');
console.log('Correct:', header2.match(/^Bearer [^B]/) !== null && !header2.includes('Bearer Bearer'));
console.log();

// Test 3: Token with "Bearer Bearer " prefix (edge case)
const token3 = 'Bearer Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature';
const cleaned3 = cleanToken(token3);
const header3 = `Bearer ${cleaned3}`;
console.log('Test 3: Token with "Bearer Bearer " prefix');
console.log('Input:', token3.substring(0, 40) + '...');
console.log('Cleaned:', cleaned3.substring(0, 20) + '...');
console.log('Header:', header3.substring(0, 30) + '...');
console.log('Correct:', header3.match(/^Bearer [^B]/) !== null && !header3.includes('Bearer Bearer'));
console.log();

// Test 4: Verify header format
console.log('Test 4: Header format validation');
const testHeader = `Bearer ${cleanToken(token1)}`;
const bearerCount = (testHeader.match(/Bearer/gi) || []).length;
console.log('Number of "Bearer" in header:', bearerCount);
console.log('Expected: 1');
console.log('Pass:', bearerCount === 1);
console.log();

console.log('=== All tests completed ===');
