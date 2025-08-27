import { index, type RouteConfig, route } from "@react-router/dev/routes";

export default [
	index("routes/index/route.tsx"),
	route("about", "routes/about/route.tsx"),
	route("summary/:issueId", "routes/summary/route.tsx"),
] satisfies RouteConfig;
