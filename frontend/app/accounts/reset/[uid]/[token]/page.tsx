import PasswordForm from '../../../PasswordForm';
export default async function Page({ params }: { params: Promise<{ uid: string; token: string }> }) {
  const { uid, token } = await params;
  return <PasswordForm uid={uid} token={token} />;
}
