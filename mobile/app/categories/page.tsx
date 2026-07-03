import MobileLayout from "../../components/MobileLayout";
import { boardProfiles } from "../../lib/board-data";
import { industryCategoriesMock } from "../../lib/mock";
import { CategoriesClient } from "./CategoriesClient";

export default function CategoriesPage() {
  return (
    <MobileLayout subtitle="免费内容" title="行业大类">
      <CategoriesClient categories={industryCategoriesMock} boards={boardProfiles} />
    </MobileLayout>
  );
}
