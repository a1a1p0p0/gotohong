import { notFound } from "next/navigation";
import { SubcategoryDetailClient } from "./SubcategoryDetailClient";
import { getCategoryById, getSubcategoryById } from "../../../lib/mock";

export default async function SubcategoryDetailPage({
  params,
}: {
  params: Promise<{ subcategoryId: string }>;
}) {
  const { subcategoryId } = await params;
  const subcategory = getSubcategoryById(subcategoryId);
  const category = subcategory ? getCategoryById(subcategory.categoryId) : undefined;

  if (!subcategory || !category) {
    notFound();
  }

  return <SubcategoryDetailClient category={category} subcategory={subcategory} />;
}
