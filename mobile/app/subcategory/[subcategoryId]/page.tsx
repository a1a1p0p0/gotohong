import { notFound } from "next/navigation";
import { SubcategoryDetailClient } from "./SubcategoryDetailClient";
import { boardProfiles } from "../../../lib/board-data";
import { getCategoryById, getSubcategoryById, industrySubcategoriesMock } from "../../../lib/mock";

export function generateStaticParams() {
  const subcategoryIds = industrySubcategoriesMock.map((subcategory) => subcategory.subcategoryId);
  const boardIds = boardProfiles.map((board) => board.boardCode);

  return [...subcategoryIds, ...boardIds].map((subcategoryId) => ({
    subcategoryId,
  }));
}

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
