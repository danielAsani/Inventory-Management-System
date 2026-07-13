import ErrorPage from "./ErrorPage";

export default function ServerError() {
  return (
    <ErrorPage
      code="500"
      title="Un incident est survenu"
      description="Veuillez reessayer dans quelques instants."
    />
  );
}
