// Test the exact same credentials outside of NextAuth
const clientId = "7732324345493-kcckla01s5h3ukagsbi4890m6dn768j0.apps.googleusercontent.com";

console.log('Testing OAuth URL construction...');
console.log('Client ID length:', clientId.length);
console.log('Client ID format valid:', clientId.endsWith('.apps.googleusercontent.com'));

const params = new URLSearchParams({
  client_id: clientId,
  redirect_uri: 'http://localhost:3000/api/auth/callback/google',
  response_type: 'code',
  scope: 'openid profile email',
  prompt: 'consent',
  access_type: 'offline'
});

const testUrl = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
console.log('\nTest this URL manually in your browser:');
console.log(testUrl);