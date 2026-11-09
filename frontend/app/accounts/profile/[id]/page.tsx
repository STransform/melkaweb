import AccountPortal from '../../../../components/AccountPortal';
import AdminLayout from '../../../dashboard/layout';
export default async function Page({ params }: { params: Promise<{ id: string }> }) { return <AdminLayout><AccountPortal id={(await params).id} /></AdminLayout>; }
