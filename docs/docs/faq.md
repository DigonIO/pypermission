---
description: "PyPermission - The python RBAC library. FAQ on design decisions, implementation details, and more about authorization in general."
---

# PyPermission - FAQ

## Why did you implement yet another authorization library?

While many experimental Python packages exist, none offered the robustness and production-ready guarantees we needed. SaaS-based solutions were available, but they introduced unwanted external dependencies and added latency which we wanted to avoid.

We tried to adopt **ory kratos**, a popular open-source RBAC software, but found its configuration and deployment experience cumbersome, especially within our development environment. Current alternatives come with similar issues, where the permission engine requires non-python native services or domain specific languages.

In one of our projects we realized a custom RBAC system on top of **SQLAlchemy**, but rather than keeping the authorization implementation tangled with business code, we decided to extract it into a standalone package. This not only allowed us to reuse the same, authorization engine across multiple projects, but also gave us an opportunity to share it with the broader Python community. The result is the **PyPermission** library you see today.

## Can I implement feature flagging with the `PyPermission` library?

Yes. Feature flagging is a use-case for RBAC. You can define a dedicated _virtual_ `ResourceType` called `featureflag`. Each feature you wish to toggle for a user is then represented as a container **Permission** under this type. You can use an empty string for the `ResourceID`.

For example, the permission `"featureflag:access_dashboard2.0"` grants a user the ability to view the experimental Dashboard 2.0 UI. All other flags follow the same pattern (`"featureflag:enable_new_payment_flow"`, etc.).

To design **Permissions** that are clear, maintainable, and extensible, please consult our [definitions](./definitions.md) page and the more detailed [permission design guide](./permission_design_guide.md).

## Is `PyPermission` fast enough for me?

Please let us know! We developed **PyPermission** on top of **SQLAlchemy** and **Python** - a database ORM and a high level language not known for boundary breaking performance. We are of the opinion, that **PyPermission** profits from the solid ecosystem this provides when it comes to static code analysis, type checking and testing. This allows us to focus on guaranteed behaviour first, before improving on performance. If you run into bottlenecks, we are happy to work with you (and open for additional sponsors).
