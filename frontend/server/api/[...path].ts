export default defineEventHandler((event) => {
  const request = getRequestURL(event)
  const target = new URL(useRuntimeConfig(event).apiOrigin)
  target.pathname = request.pathname
  target.search = request.search

  return proxyRequest(event, target.toString())
})
