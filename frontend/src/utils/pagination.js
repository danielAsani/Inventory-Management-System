export function normalizePage(data) {
  if (Array.isArray(data)) {
    return { count: data.length, page: 1, perpage: data.length || 10, totalPages: 1, results: data };
  }

  return {
    count: data?.count ?? 0,
    page: data?.page ?? 1,
    perpage: data?.perpage ?? data?.results?.length ?? 10,
    totalPages: data?.total_pages ?? 1,
    results: data?.results ?? [],
  };
}
