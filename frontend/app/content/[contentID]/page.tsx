interface PageProps {
  params: { contentId: string };
}

export default function ContentDetailPage({ params }: PageProps) {
  return (
    <div>
      <h1 className="text-2xl font-bold">Content: {params.contentId}</h1>
      <p className="text-gray-600">Editor or viewer will go here.</p>
    </div>
  );
}
