import ErrorPage from "./ErrorPage";

export default function NotFound() {
  return (
    <ErrorPage
      code="404"
      title="Page introuvable"
      description="La page que vous recherchez n'existe pas ou a ete deplacee."
    />
  );
}
