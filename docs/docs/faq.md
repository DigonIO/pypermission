---
description: "PyPermission - The python RBAC library. FAQ on design decisions, implementation details, and more about authorization in general."
---

# PyPermission - FAQ

## Why we developed the `PyPermission` library?

While many experimental Python packages exist, none offered the robustness and production-ready guarantees we needed. SaaS-based solutions were available, but they introduced unwanted external dependencies and added latency which we wanted to avoid.

We tried to adopt **ory kratos**, a popular open-source RBAC software, but found its configuration and deployment experience cumbersome, especially within our development environment.

In one of our projects we realized a custom RBAC system on top of **SQLAlchemy**. Rather than keeping that logic tangled with business code, we extracted it into a standalone package. This not only allowed us to reuse the same, authorization engine across multiple projects, but also gave us an opportunity to share it with the broader Python community. The result is the `PyPermission` library you see today.

## Can I implement feature flagging with the `PyPermission` library?

Yes. Feature flagging is a use-case for RBAC. You can define a dedicated _virtual_ `ResourceType` called `featureflag`. Each feature you wish to toggle for a user is then represented as a container Permission under this type. You can use an empty string for the `ResourceID`.

For example, the permission `"featureflag:access_dashboard2.0"` grants a user the ability to view the experimental Dashboard 2.0 UI. All other flags follow the same pattern (`"featureflag:enable_new_payment_flow"`, etc.).

To design permissions that are clear, maintainable, and extensible, please consult our [definitions](./definitions.md) page and the more detailed [permission design guide](./permission_design_guide.md).
