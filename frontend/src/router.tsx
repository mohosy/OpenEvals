import { Outlet, createRootRoute, createRoute, createRouter } from "@tanstack/react-router";

import { AppLayout } from "./components/AppLayout";
import { HomeRoute } from "./routes/home";
import { NewSuiteRoute } from "./routes/new-suite";
import { RunRoute } from "./routes/run";
import { SuiteRoute } from "./routes/suite";

const rootRoute = createRootRoute({
  component: () => (
    <AppLayout>
      <Outlet />
    </AppLayout>
  ),
});

const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: HomeRoute,
});

const newSuiteRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/suites/new",
  component: NewSuiteRoute,
});

const suiteRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/suites/$suiteId",
  component: SuiteRoute,
});

const runRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/runs/$runId",
  component: RunRoute,
});

const routeTree = rootRoute.addChildren([homeRoute, newSuiteRoute, suiteRoute, runRoute]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

