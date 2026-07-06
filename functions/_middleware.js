// Cloudflare Pages middleware.
//
// Both softwaremanager.xyz and vstsearch.softwaremanager.xyz serve the same
// index.html. Crawlers (Discord, Twitter, etc.) read the raw HTML and do NOT
// run JavaScript, so we rewrite the <title> and Open Graph / Twitter meta tags
// server-side when the request is for the VST Search subdomain. This gives the
// subdomain its own link embed without a separate deploy.

const VST = {
  title: "VST Search - SoftwareManager",
  description: "Search for plugins easily",
  url: "https://vstsearch.softwaremanager.xyz/",
};

class AttributeSetter {
  constructor(attribute, value) {
    this.attribute = attribute;
    this.value = value;
  }
  element(element) {
    element.setAttribute(this.attribute, this.value);
  }
}

class ContentSetter {
  constructor(value) {
    this.value = value;
  }
  element(element) {
    element.setInnerContent(this.value);
  }
}

export async function onRequest(context) {
  const { request, next } = context;
  const response = await next();

  const onVstDomain = new URL(request.url).hostname.startsWith("vstsearch.");
  const contentType = response.headers.get("content-type") || "";

  // Leave everything untouched on the main domain and for non-HTML responses.
  if (!onVstDomain || !contentType.includes("text/html")) {
    return response;
  }

  return new HTMLRewriter()
    .on("title", new ContentSetter(VST.title))
    .on("meta[name='description']", new AttributeSetter("content", VST.description))
    .on("meta[property='og:title']", new AttributeSetter("content", VST.title))
    .on("meta[property='og:description']", new AttributeSetter("content", VST.description))
    .on("meta[property='og:url']", new AttributeSetter("content", VST.url))
    .on("meta[name='twitter:title']", new AttributeSetter("content", VST.title))
    .on("meta[name='twitter:description']", new AttributeSetter("content", VST.description))
    .transform(response);
}
