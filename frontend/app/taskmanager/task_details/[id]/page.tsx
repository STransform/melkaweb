import Tasks from '../../Tasks';
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  return <Tasks id={(await params).id} />;
}
