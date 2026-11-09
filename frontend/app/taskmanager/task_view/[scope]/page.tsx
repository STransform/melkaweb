import Tasks from '../../Tasks';
export default async function Page({ params }: { params: Promise<{ scope: string }> }) {
  return <Tasks scope={(await params).scope} />;
}
