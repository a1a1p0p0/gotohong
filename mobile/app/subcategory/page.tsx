import { SubcategoryPaidClient } from "./SubcategoryPaidClient";

export default async function SubcategoryPage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string; subcategory?: string }>;
}) {
  const params = await searchParams;

  return (
    <SubcategoryPaidClient
      initialCategoryId={params.category}
      initialSubcategoryId={params.subcategory}
    />
  );
}
