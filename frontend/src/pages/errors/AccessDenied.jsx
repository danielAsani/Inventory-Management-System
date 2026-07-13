import ErrorPage from "./ErrorPage";

export default function AccessDenied() {
  return (
    <ErrorPage
      code="403"
      title="Acces non autorise"
      description="Votre compte ne dispose pas des autorisations necessaires pour acceder a cette page."
    />
  );
}
