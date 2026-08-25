# fun with migasfree

# Preface

## Acknowledgments

Behind every project, there are people who make it possible—maintaining, encouraging, correcting, collaborating, supporting…

I would like to express my gratitude first to Eduardo Romero. He gave me the necessary encouragement to release the first version of migasfree, making this project visible on the Internet. He also made the first and only donation that migasfree has received (even though it was for a lost bet, I didn’t hold it against him, and it was very well received), allowing us to pay for a year of the [migasfree.org](https://migasfree.org) domain.

I am also grateful to [Jose Antonio Chavarría](https://github.com/jact), my companion in hardships (and joys). He has been and continues to be a cornerstone of migasfree. He has substantially improved the project by rewriting spaghetti code into good code , contributing ideas and solutions. He calms me down when I want to rush, and he is the guardian of migasfree’s simplicity.

*  A process known very locally as *chavarrización*.

To Jesús González for his commitment to creating work teams where people feel comfortable working.

To the entire User Support group of the Zaragoza City Council, and especially the Free Software team. It was a true pleasure to work with them, and they made me laugh every single day.

I would also like to thank Arturo Martín and Ignacio Sancho, from the [Vitalinux](https://docs.vitalinux.educa.aragon.es/) project, for their constant willingness to support any idea I propose, however unusual it may be, and for being the greatest enthusiasts of migasfree. Their dedication and trust make them very special people to me.

To [Thoti](https://thotigacias.blogspot.com/), for all his support and ingenuity. He’ll just as easily take a photo for this book as he will print the migasfree logo on a t-shirt, or surprise you with a unique and original wood-burned beer mug to be given as a prize at the [migascon 2022](https://migasfree.org/migascon-2022.html). Thank you for always being attentive to needs.

To Iker Ibarguren from [Pasaiako Udala](https://www.pasaia.eus/eu/), Rafael Gaioso from [Concello de Santiago de Compostela](https://santiagodecompostela.gal/es), Carlos González and Jordi Román from the [Universitat Autònoma de Barcelona](https://www.uab.cat/) for their translations into Basque, Galician, and Catalan. Eskerrik asko, grazas & gràcies.

To Gorka González for allowing me to write the [Success case of migration to GNU/Linux of the Pasaia City Council](https://migasfree.org/blog/2019/2019-03-11-zorionak-pasaia.html).

And finally, I want to express my gratitude to the entire Free Software community in general, for the valuable knowledge they have provided me and for their wonderful products that I use daily.

We always receive more than we give. Thank you from the bottom of my heart!

\

## About me

From a very young age, I felt a deep fascination for programming. It started with a small device called [ZX Spectrum](https://en.wikipedia.org/wiki/ZX_Spectrum).

As a young person, I was drawn to programming. I studied electronics, where I learned to program the [8751 microcontroller](https://en.wikipedia.org/wiki/MCS-51) in machine code.

I worked as an electronics technician in my early career, and shortly after, with the boom of personal computing, I started developing applications of all kinds.

I have worked as an employee, as an entrepreneur, as a freelancer, and finally as a civil servant in local administration, although in the meantime, I also learned how difficult it is to face the lack of employment.

I was part of the Free Software team of the Zaragoza City Council, where I developed and maintained AZLinux, the free desktop now used by 80% of municipal workers. This project, which gave rise to migasfree, has established itself as a benchmark for migration to Free Software in Spanish public administration, thanks to the tenacity of those of us who were part of this team.

Currently, my work at the Zaragoza City Council focuses on the automation of all kinds of processes, ranging from server and user management to working with containers, protocols, certificates, APIs, services, communication devices…

I continue to dedicate part of my free time to ensuring that migasfree keeps evolving, not just as software, but as a methodology that allows systems to “breathe” and adapt on their own.

I also enjoy listening to music, the smell of wet earth, and being made to laugh at any silly thing.

I also enjoy contemplating the sky on summer nights, silently repeating the names of the stars and constellations that my father taught me to recognize and locate in the firmament when I was a teenager: Vega, Altair, Deneb, Cassiopeia, the Big Dipper, the Little Dipper, Polaris… Doing so, I feel his presence still accompanies me, as in those days when, from the long and narrow balcony of the house, he would extend his arm to point with his index finger at a tiny point of light, barely visible through the haze of light pollution. “Altair, another of [the three beauties](https://en.wikipedia.org/wiki/Summer_Triangle)!” he would say, and then remain motionless, pointing, patient, while I struggled to locate that elusive flash with narrowed eyes.

In the same way my father did with me, I loved sharing with Jesús the little I remembered from my electronics studies when he was a small child: A LED!… A diode!… [A 555 integrated circuit](https://en.wikipedia.org/wiki/555_timer_IC), the electronic pill!, I would tell him while placing it in his little hand. Later, he would strive to plug the [arduino nano](https://en.wikipedia.org/wiki/Arduino_Nano) into a breadboard for the burgundy red papier-mâché star that would decorate the Christmas tree that year. While he tried, I waited patiently for him to get it right.

We name the stars and teach them to our children; we leave a little pile of silicon ash in their small hands, themselves made of ashes resulting from [stellar nucleosynthesis](https://en.wikipedia.org/wiki/Stellar_nucleosynthesis). We kindly spend our time… to clumsily, and with four hands, perch a papier-mâché red giant at the very top of the Christmas tree.

> “Something in us recognizes the Cosmos as its home. We are made of starstuff.”

Now Jesús is passionate about mathematics, especially [topology](https://www.youtube.com/watch?app=desktop&v=Qaa5nN_xzoE&t=0s); I thoroughly enjoy learning from him, but above all I adore his company.

\
\
\
\
\
\

## Author’s note

Some have criticized those of us who dedicate our time to producing free software. The argument claims that our contribution destroys jobs or prevents companies from doing business due to unfair competition. They claim to be tired of people who “work for free” and “take away” their livelihood.

I cannot agree. First of all, because [free software](https://www.gnu.org/philosophy/free-sw.html) is not an economic issue; rather, it simply raises a question of **freedom**.

I believe that obsolete business models must adapt and evolve into new ways of generating wealth, creating new relationships between producer and consumer. Business models based on free software often point us in the right direction, as they establish these new relationships and gain the trust and recognition of consumers, not precisely for economic reasons. Don’t companies want this for themselves?

Regarding the idea that producing something that others obtain for free does not generate jobs, I believe it is false. One only needs to look at how interconnection technologies, protocols, and accessibility services of the Internet have generated, and will continue to generate, countless jobs. I am convinced that the Internet would not even be a shadow of what it is today if these technologies had been patented, closed, and/or economically exploited.

I believe that the free software movement, together with others like [devolucionism](https://lasindias.net/indianopedia/Devolucionismo), represents a hope for Knowledge to be produced again by society and for society, in contrast to the Knowledge created, marketed, and controlled by certain organizations, which sometimes harms society.

\

## Structure

**I. Fundamentals**

> In this first part, we will review Software Configuration Management. Understanding the basics of this Software Engineering process will give you an overview that I consider essential because this is precisely where migasfree is integrated.

> I will explain the difficulties that a desktop administrator will encounter and how they can be easily overcome, drawing on the experience gained in AZLinux.

> You will be able to learn about the history, features, and components used by migasfree.

**II. Getting Started**

> Here, I will show you how to install and test a migasfree server and client with the minimum configuration so that you can see them in operation as soon as possible.

**III. Administration**

> It will let you learn about both the migasfree client and server in more detail, delving into service orchestration, the web console, deployments, the client environment tools (client, agent and visual catalogue), the Windows environment, master images and data.

**IV. Production**

> It covers the principles and procedures that guarantee robust operation in real environments: high availability, sizing, backups, maintenance and observability.

**V. Settings**

> It details the necessary settings to properly configure both the migasfree server and the clients.

**VI. Annexes**

> It contains supplementary guides on migration between legacy versions, automation through the migasfree REST API, integration with AI assistants, a reference of the command-line commands and the reference glossary. The latter gathers the technical terms used throughout the book, linked from the text itself so you can look up their definition with a single click.
\

## License and Copyright

> Fun with migasfree

> Copyright (C) 2013 - 2026 Alberto Gacías and contributors.
> Permission is granted to copy, distribute and/or modify this document
> under the terms of the GNU Free Documentation License, Version 1.3
> or any later version published by the Free Software Foundation;
> with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
> A copy of the license is included in the section entitled “GNU
> Free Documentation License”.

## Links

* [HTML version](http://fun-with-migasfree.readthedocs.org/).

* [PDF version](https://media.readthedocs.org/pdf/fun-with-migasfree/master/fun-with-migasfree.pdf).

* [Examples used in the book](https://github.com/migasfree/fun-with-migasfree-examples/).

* [Source code](https://github.com/migasfree/fun-with-migasfree/).

* [Migasfree project](http://migasfree.org/).

* X: [@migasfree](https://twitter.com/migasfree), [@albertogacias](https://twitter.com/albertogacias).

# I. Fundamentals

In systems administration, challenges are constant. From configuration management and security patch deployment to resource optimization, incident resolution, or auditing, administrators must adapt to an insecure and complex environment, full of incompatibilities and continuous changes.

Mastering **Software Configuration Management** (SCM), a fundamental process in Software Engineering, is crucial for both developers and systems administrators. This process ensures that software is developed, maintained, and delivered in a controlled, precise, and organized manner, reducing errors and guaranteeing the traceability of all changes. Furthermore, it allows for the systematic management of versions, configurations, and modifications of software items throughout their entire lifecycle.

The history of SCM dates back to the 1950s when it was initially applied to hardware development. As software complexity grew, so did configuration management techniques and tools. Thus, SCCS appeared in 1972. Later, CVS in 1986 and Subversion in 2000, both tools considered obsolete today. Starting in the 2000s, distributed version control systems emerged, such as [Git](https://git-scm.com/) in 2005, which is currently the de facto standard.

We currently cannot conceive of software development without Continuous Integration (CI) and Continuous Deployment (CD), processes that emerged in the late 1990s, but it was not until the early 2010s that they became popular. Since then, tools have evolved significantly, integrating seamlessly with code repositories such as [GitHub](https://github.com/) and [GitLab](https://about.gitlab.com/).

**migasfree** emerged influenced by these ideas and trends. It is a solution that simplifies software deployment and configuration management in large and complex environments, delivering and controlling software along with its configurations so that it deploys them automatically right where they are needed.

In this first part, we will talk about SCM and explore the history behind migasfree, its most relevant features, and the components that have made migasfree a sort of “rara avis” in the systems management field. And I say “rara avis” because in contrast to other “birds”, migasfree invents nothing, but simply makes use of the greatest contribution that Free Software has made to the Software Industry: package management systems.

I want to offer you not only a technical guide, but also inspiration to generate and embrace change in your day-to-day work.

Shall we start?

# Introduction

*Hi. I’m Alberto Gacías. Welcome to the first chapter of “Alberto Gacías presents fun with migasfree”. Over the next few pages, we are going to explore the dynamic world of migasfreelogy together.* 

*  Recalling Sheldon Cooper in “Fun with Flags” in The Big Bang Theory series.
\

## Target Audience

This book is designed to be a practical guide for workstation and server administrators looking to improve the customization and management of their machines. If your goal is to manage computers efficiently, while guaranteeing the integrity of software changes, you will find this book useful.

Here you will find an introduction to using migasfree, from basic concepts to practical applications in real environments. The content evolves along with the software, so if you downloaded this book a while ago, some sections may no longer be up to date. We recommend that you always check the most recent version to make the most of the improvements and features that have been incorporated.

This material is designed to help you get the most out of migasfree, regardless of the size of your IT park or the specific needs of your work environment.

\

## What is migasfree?

In a few words: **a deployment manager**.

[migasfree](https://migasfree.org) specializes in the automated and centralized deployment of applications and configurations across a computer park, optimizing the process and eliminating the complexity of managing them manually.

To understand it better, imagine that migasfree acts like a **smart logistics and delivery system** that transports your **packages** (applications and configurations) right to the door of each of your **computers**. Like an automated delivery fleet, it does not just ship boxes in bulk: it inspects the profile of each recipient, selects exactly what each workstation needs, and plans the ideal delivery time to guarantee an efficient, orderly supply without saturating the network.

The secret to such **delivery precision** lies in the **attributes**, the authentic **DNA of each computer**. These attributes are obtained through **formulas**—small programmable code snippets that run on the client—allowing each computer to communicate its specific profile and automatically receive the exact configurations it needs.

This is the philosophy we apply in [AZLinux](http://zaragozaciudad.net/azlinux/), the free desktop migration project of the [Zaragoza City Council](http://zaragoza.es), where migasfree has become indispensable. After years of experience, I am convinced that it is the definitive solution for managing any IT park with elegance and efficiency.

\

## What does it do?

migasfree uses package systems to implement any changes to the software, guaranteeing that they are carried out in a controlled and reliable manner.

This approach ensures the integrity of the entire process, providing confidence and precision in management. Its unique method clearly distinguishes it from other systems administration tools, offering a robust and efficient solution.

Its main functions are:

> * **Centralized computer management**: Administrators can perform tasks such as installations, updates, configurations, and systems monitoring without the need for direct intervention on each computer, saving time and resources.
> * **Scheduled and segmented software deployment**: One of the key features of migasfree is the ability to deploy software in a planned manner. Administrators can schedule installations or updates for specific times and define conditions based on the characteristics of the computers or users. This ensures that software changes reach the right machines at the right time.
> * **Computer control and customization while maintaining integrity**: Allows administrators to customize configurations on machines, from system settings to user preferences. Despite this flexibility, the system ensures the integrity of the machines, avoiding configuration conflicts or failures derived from unauthorized customizations.
> * **Hardware and software auditing**: Provides an up-to-date inventory of the computer park. The system automatically audits the installed hardware and software, providing highly accurate data for each computer.
> * **Automated printer installation**: Simplifies printer management, automating their installation in a centralized manner. Administrators can assign specific printers to computers, reducing the time and issues associated with manual configurations.
> * **Centralized deployment error management**: Centralizes error management for package managers, allowing administrators to identify and resolve issues efficiently and proactively.
> * **Hardware and software faults**: Monitors machine faults. Administrators can detect hardware or software issues in time and apply fixes remotely, which improves operational continuity.
> * **Applications**: End users can manually install or uninstall the applications that the organization makes available to them, without needing to be machine administrators. The experience is intuitive, as each user can clearly view the applications specifically published for them by the organization. This ensures easy and controlled access to software authorized by the company.

In summary, migasfree centralizes and modernizes computer management. It allows for the automation of repetitive tasks, significantly reducing the need for manual intervention, which increases operational efficiency. Its unique approach using package systems guarantees integrity. Finally, it offers full control thanks to its ability to provide complete visibility and supervision of the IT park.

\

## How does it work?

The idea that makes migasfree a powerful tool is simple.

In a standard GNU/Linux system, such as one you might install at home, the configuration of the repositories accessed by the package manager is **static**—that is, it does not usually change once configured.

For example, in a distribution like Debian, repositories are configured in files like `/etc/apt/sources.list`. In a standard environment, this repository definition remains practically unchanged over time.

> ```text
> $ cat /etc/apt/sources.list

> deb http://deb.debian.org/debian trixie main non-free-firmware
> deb http://security.debian.org/debian-security trixie-security main non-free-firmware
> deb http://deb.debian.org/debian trixie-updates main non-free-firmware
> ```

However, in a GNU/Linux system with the migasfree client installed, the repository configuration is **dynamic**. On each synchronization, the client sends its **attributes** to the server, which immediately calculates which sources and actions correspond to that specific workstation.

The client immediately reconfigures its software sources by combining two levels:

* **External repositories**: Official sources of the distribution or external providers, with traffic optimized through the **cache** provided by migasfree.
* **Internal repositories**: Generated by the migasfree server itself from the software we upload to the platform (both our own packages and third-party ones that lack an online repository).

Finally, the client performs the appropriate updates, installations, or uninstallations using the native package manager of the operating system.

This approach allows the infrastructure to stop being a rigid set of machines and instead adapt continuously and automatically to the characteristics and changes of each workstation.

It is surprising to see how such a simple idea can transform the work of administrators, simplifying it significantly. migasfree allows us to focus exclusively on the software changes to be made, and on defining precisely to whom or to which computers they apply. This combination of simplicity and efficiency not only saves time and resources, but also makes software management a much more agile and effective process.

\

To show you how it changes the way administrators act, let me tell you about an experience from the early days of the migration from Windows to AZLinux, when migasfree did not yet exist.

One of the problems we faced was with a very old graphics card model. To avoid failures, we had to place a special configuration file in a specific path. Every time we found a computer with that card, the situation was usually as follows:

> - “Hey, what did we need to do with the strange graphics card?”
> - “I don’t remember. It’s documented somewhere. Look it up.”

Does that sound familiar? I’m sure it does.

One of our first packages was, precisely, the configuration for that graphics card. Simply installing it solved the issue. Although the question had changed, the underlying problem was still there:

> - “Hey, what was the package for the strange graphics card called? I need to install it.”
> - “I don’t remember. Look it up.”

Although we had made significant progress by avoiding manual file creation, which is error-prone, there was still work to be done on this matter.

When we started using migasfree, we configured it so that any computer with that “devil’s card” would automatically have our package deployed. In this way, we eliminated the problem at its source: there was no longer any need to search or remember anything.

Since then, we focus on **solving** the issue raised by **packaging the software change** and **automating its deployment**. We forget about the rest, because we know migasfree will do it.

Every time I tell it, it reminds me of this phrase commonly attributed to Einstein: “An intelligent person solves the problem; a wise person avoids it.”

\

## Summary

migasfree does not reinvent the wheel: once the change is packaged, it **automates its deployment**, allowing operating systems to adapt on their own.

I invite you to navigate between the theory and practice of migasfree. We will walk together from the foundations of configuration management to the operation of a real production park, are you in?

# Software Management

> > Nothing is permanent except change.

We are used to periodically updating our applications: systems quickly become obsolete, new technologies appear, bugs are resolved, and new needs emerge. No matter what stage of the system’s lifecycle we are in, the system will change, and the desire to change it will persist throughout its entire lifecycle. 

*  First law of Systems Engineering, Software Configuration Management, Bersoff, Henderson & Siegel, Prentice-Hall, 1980

Therefore, software change is both **inevitable** and **desirable**.

It is inevitable: we make mistakes and correct them with a modification. We call these types of changes **corrective**.

On the other hand, change is desirable: we often want to incorporate new features or improve existing ones, and we do so through **evolutionary** changes.

Change generates **confusion** and uncertainty, and it occurs from the moment we conceive, build, and also while we maintain a software project.

The great challenge lies precisely in managing changes in a controlled manner and maintaining system integrity through a strategy that facilitates both change management and configuration in general.

This is what **Software Configuration Management** (SCM) is about, a key process within Software Engineering that identifies, tracks, controls system components, and manages the changes that occur in them.

In this chapter, you will understand what it means to manage software in an orderly fashion. You will see the principles, methodologies, and tools that keep a project under control from its design to its evolution.

\

## Software Configuration

Every software system is, at any given moment, a set of pieces. We call this snapshot of the system at a specific moment the **Software Configuration** (SC): source code, documentation, scripts, binaries, libraries, test data… everything needed to build, deploy, operate, and maintain it.

In essence, SC encompasses:

> * Software components: Source code, libraries, and binaries.
> * Documentation: User manuals, installation guides, technical specifications, etc.
> * Support tools: Scripts, development environments, and configurations.
> * Associated data: Configuration files, initial databases, test data.

The SC forms the basis on which **Software Configuration Management** (SCM) relies, a process that ensures that every change, version, or variation of the software is tracked and managed without inconsistencies or errors, both in development and maintenance.

As a fundamental part of Software Management, SCM focuses on the control, tracking, and management of configurations and changes in its components. Its goal is to maintain **integrity** and **control** over software products throughout their lifecycle, so that all pieces, versions, and states of the artifacts are organized, identifiable, and traceable.

The scope of SCM is extensive and includes:

> * Version control and system configuration as a whole.
> * Identification and labeling of components.
> * Management of dependencies between modules or components.
> * Monitoring of changes in all project assets.
> * Automation of deployment, testing, and integration.

**SCM is not limited** to maintaining the integrity and control of components **only until their release**, as is common in operating systems where the manufacturer manages SCM only to that point. Organizations must implement their own SCM to manage software deployment and configuration on end systems. This process goes beyond simply controlling versions and configurations; it also involves ensuring that every change, update, or new application is deployed precisely and consistently on the devices, respecting the specific needs of each one and guaranteeing that the software is deployed effectively in the work environment.

From a systems architecture perspective, this approach marks the transition from an **imperative** model (where we give step-by-step commands) to a **declarative** model. In the declarative model, the administrator defines the “desired state” of the system, and it is SCM, supported by tools like migasfree, that ensures reality converges with that definition.

\

## Integrity

In the context of SCM, when we talk about integrity, we refer to the accuracy, consistency, and reliability of software elements throughout their entire lifecycle. This includes ensuring that source code, build artifacts, configurations, and any other related components are complete, have not been modified without control, and can be tracked and managed effectively.

Integrity in SCM has several key aspects:

> * **Version control**: Ensures that all modifications to the source code and other software artifacts are recorded, allowing to know what changes were made, when, and by whom, so that it can be reverted to previous versions if necessary. This prevents the software from becoming corrupted or losing information.
> * **Protection against unauthorized changes**: Code and artifacts are protected from unwanted or malicious changes. Only individuals with appropriate permissions can modify configurations or code, and every change is recorded for subsequent auditing.
> * **Build consistency**: Guarantees that, starting from a specific version of the source code and configurations, the software build process is always the same, meaning the built software will be consistent and free of bugs that might appear due to differences in component versions or configurations.
> * **Audit and traceability**: Through change management, integrity is also ensured by the traceability of decisions and modifications made to the software, allowing for a complete audit of its evolution.

In summary, integrity in SCM is fundamental to maintaining reliability and control over software elements, ensuring that changes are traceable, authorized, and consistent throughout all phases of the software lifecycle.

\

## Change Control

**Change control** (CC) is the **systematic management** of modifications in products, systems, or processes, used in industries like manufacturing and software development. It includes procedures to identify, evaluate, approve, implement, and monitor changes, minimizing risks, guaranteeing proper documentation, and ensuring quality, reliability, and regulatory compliance.

The **Change Control System** (CCS) is a **set of processes, policies, and tools** used to manage changes in a system, ensuring they are implemented in a controlled, orderly, safe, and documented manner. Its main purpose is to maintain the integrity, stability, and coherence of the system while adapting to new needs, requirements, or fixes.

The fundamental difference between SCM (Software Configuration Management) and CCS (Change Control System) lies in their scope and purpose within software management. While **SCM** focuses on the **integral management** of the system configuration, encompassing **all artifacts** (source code, documentation, testing, configurations) and ensuring consistency, traceability, and version control throughout the software lifecycle, the **CCS** has a **more specific focus**: managing **individual changes** requested within the system, evaluating their impact, obtaining necessary approvals, and ensuring they are implemented in a controlled manner. In simple terms, SCM oversees the system in its entirety and its evolution over time, while CCS is a process within SCM dedicated exclusively to changes and their correct incorporation.

|               | **SCM**                                                   | **CCS**                                            |
|---------------|-----------------------------------------------------------|----------------------------------------------------|
| **Purpose**   | Manage complete configurations and versions               | Manage specific changes                            |
| **Scope**     | All artifacts                                             | Change requests and approval                       |
| **Process**   | Identifies, tracks, and manages project components        | Evaluates, approves, and applies changes           |
| **Timeframe** | Continuous management of the entire software lifecycle    | Cycle of a specific change from request to closure |
| **Changes**   | Tracks the impact of changes on the overall configuration | Manages the processes to make changes              |
\

To maintain a controlled system and preserve its integrity, it is essential to adopt a structured approach that effectively manages changes and dependencies. Key points are:

> * **Controlled management**: Changes must follow a formal workflow with reviews and approvals before implementation.
> * **Impact assessment**: Analyze the potential effects of changes on the system, considering functional, technical, and operational aspects.
> * **Clear traceability**: Associate each change with requirements, incidents, or improvements, and maintain a historical record of requests, approvals, and implementations.
> * **Thorough testing**: Validate changes to ensure they meet requirements without introducing errors, using unit, integration, regression, and acceptance tests.
> * **Proper documentation**: Record all details of the change and update system documentation.
> * **Dependency management**: Identify and evaluate how changes affect other components, planning their implementation to avoid conflicts and maintain stability.

In conclusion, a system will remain integral through a change if:

> * it is managed in a controlled manner,
> * its impact is assessed,
> * it is clearly tracked,
> * it is properly tested,
> * it is correctly documented,
> * and dependencies are managed to ensure its success.
\

## CCS Tools

Change Control System (CCS) tools make up a broad and diverse set of solutions designed to optimize every stage of software development and maintenance. These tools allow for managing code versions, automating testing, facilitating integrations and deployments, and ensuring consistency and stability across different environments. Their diversity lies in their ability to adapt to the specific needs of projects, ranging from version control systems that track and revert changes, to advanced continuous integration and deployment platforms that guarantee automated and efficient workflows. In addition, they include project and configuration management tools, essential for maintaining organization, traceability, and software quality throughout its lifecycle. This comprehensive ecosystem is key to facing modern development challenges and fostering collaboration among teams.

> * **Version Control Systems (VCS)**:
>   * Git, Subversion, or Mercurial allow for recording, tracking, and reverting changes in the code.
> * **Continuous Integration and Continuous Deployment Tools (CI/CD)**:
>   * GitLab CI, Jenkins, and CircleCI ensure that changes are tested and integrated frequently and in a controlled manner.
> * **Change Management Systems or Project Managers**:
>   * Redmine, Jira, Azure DevOps, or Trello structure and monitor requests and approvals.
> * **Configuration Management**:
>   * Tools like Ansible, Chef, or Puppet provide consistency across environments.
>   * In some specific projects (workstation and/or server operating systems), the **migasfree** tool is used, a solution that offers a unique approach to guarantee the consistency and traceability of changes, integrating seamlessly with the workflow of the team in charge of change control (CCS). This is mainly achieved by using Package Management Systems as tools for deploying changes.
\

## CCS Process

The CCS (Change Control System) process is a set of activities that will allow us to guarantee the integrity of the managed software. This process can be summarized into three main activities:

* Change request.
* Change.
* Release.

### Change request

It is the formal process for proposing a change in a software component.

It can include a variety of details to ensure that the change is well understood, evaluated, and managed efficiently.

> 1. **Basic Information**
>    * Change ID: A unique identifier to track the request.
>    * Request Date: Date when the request was sent.
>    * Requester: Person or team requesting the change.
>    * Change Title: Brief description or title identifying the change.
> 2. **Change Description**
>    * Change Summary: Clear and concise detail of the proposed change.
>    * Reason for Change: Explanation of why the change is necessary (for example, fixing a bug, improving performance, or meeting a client requirement).
>    * Scope of Change: What parts of the system will be affected (specific modules, databases, interfaces, etc.).
> 3. **Change Impact**
>    * Technical Impact: Assessment of how the change will affect the architecture, design, code, or technical components.
>    * Business Impact: How it will influence business goals, timelines, and costs.
>    * End-User Impact: Possible disruptions or changes to the user experience.
> 4. **Risk Analysis**
>    * Associated Risks: Identification of technical, operational, or security risks related to the change.
>    * Risk Mitigation: Strategies to minimize or eliminate the risks.
> 5. **Requirements**
>    * Resources Required: Time, tools, staff, budgets.
>    * Dependencies: Other changes, components, or teams on which the implementation depends.
>    * Constraints: Technical, time, or budget limitations that must be considered.
> 6. **Evaluation**
>    * Time Estimate: Timeframe required to develop, test, and implement the change.
>    * Estimated Cost: Budget needed to complete the change.
>    * Priority: Classification in terms of urgency (high, medium, low).
>    * Current Status: For example, pending, under review, approved, rejected.
> 7. **Approvals**
>    * Required Approvers: List of individuals or committees responsible for approving the change.
>    * Decision Log: Date and details of the approval or rejection, including comments from the change control board (CCB).
> 8. **Implementation Plan**
>    * Tentative Schedule: Key dates for each phase of the change (development, testing, implementation).
>    * Reversibility: Plan to roll back the change in case of failure.
> 9. **Traceability**
>    * References: Links to related requirements, test cases, incidents, or tickets in the project management system.
>    * Change History: Record of previous modifications to the same component, if applicable.

This level of detail helps guarantee that all stakeholders have the necessary information to make informed decisions and coordinate the change implementation effectively.

However, this level of detail must be **adapted to the complexity** of each change. For minor, routine, or low-impact modifications (UI tweaks, trivial bug fixes, or configuration updates), a simplified procedure or version control itself is usually enough. Reserving the comprehensive form for complex or critical changes optimizes team resources and avoids unnecessary bureaucracy, facilitating agility in software development and maintenance.

Below, we will explore the essential steps that must be followed when a user reports a bug or requests an improvement:

> 1. **Identify** the **Software Configuration Item** (SCI) it refers to.

>    An SCI is any software object subject to SCM. It can be a user manual, a specification, a set of test data, an application, a library, or even the tools used to make changes. The identification must be recorded in the Change Request.
> 2. Analyze the Change Request to determine its **feasibility**:
>    * In case of **Approval**: **Assign** to a person or a team.
>    * In case of **Rejection**: **Close** the Request explaining the reason for rejection.
>    * In case of **Postponement**: Record the **reason** for postponement, and under what **conditions** it will be implemented.
> 3. **Prioritization**: Approved changes are classified according to their importance and urgency.

### Change

The change is the activity that involves modifying the SCI to generate a **new version** of it.

The activities performed in this phase are:

1. **Planning and Implementation**
   * **Implementation Plan**: A detailed plan is created that includes specific tasks, resource allocation, schedule, and dependencies.
   * **Development and Testing**: Developers make modifications to the code. Rigorous tests (unit, integration, system) are applied to guarantee that the change meets requirements and does not introduce new issues.
2. **Verification and Validation**
   * **Acceptance Testing**: Changes are reviewed by the client or the responsible team to confirm they meet expectations.
   * **Documentation**: All relevant documentation is updated, including manuals, technical specifications, and changelogs.

### Release

A **release** consists of placing the **new version of the SCI** in a repository or store, so that users or clients can access and install it.

It is crucial to distinguish between release and deployment:

* **Release**: Putting the new version in an accessible place (for example, in a repository).
* **Deployment**: Installing and activating that version in the environment where it will be used (such as a production server).

That is: release ensures the version is available, while deployment puts it into operation.

The tasks corresponding to this activity are:

> 1. **Integration**: The change is merged into the main system, often through continuous integration (CI) practices.
> 2. **Production Implementation**
>    * **Deployment**: The change is deployed to the production environment using strategies like incremental deployments or version switching.
>    * **Monitoring**: The system is supervised to identify and resolve unforeseen issues that may arise after the change.
> 3. **Tracking and Closure**
>    * **Post-Implementation Evaluation**: The impact of the change on the system and the business is reviewed, and lessons learned are documented.
>    * **Change Closure**: The request is marked as completed and archived for future reference.

### Other activities of the process

Although these three activities represent the basic core of the CCS process, in complex projects SCM encompasses much more, including:

* **Configuration identification**: Defining and recording the elements that form the system’s baseline configuration before implementing changes.
* **Configuration control**: Establishing policies and procedures to ensure only authorized changes are made.
* **Audits and reports**: Verifying that changes are implemented correctly and comply with established standards. This includes guidelines for testing, monitoring, and confirming their effectiveness.
* **Version and variant management**: Managing different versions of the software adapted to different environments or clients.

\

## SCI

A Software Configuration Item (SCI) is any component or software unit managed and controlled throughout its lifecycle by the SCM discipline.

The characteristics defining an SCI are:

* **Identifiable**: It has a unique name or identifier that allows distinguishing it from other items.
* **Controlled**: Its versions, changes, and relationships with other elements are managed.
* **Traceable**: Its origin, evolution, and relationships with other elements in the system can be tracked.
* **Versionable**: It can have multiple versions associated with different stages of development.

If we look at how different Free Software projects perform SCM, we see they perform the mentioned activities, finally releasing the project’s source code on the Internet.

These projects work with different types of SCIs (.png, .txt, .py, .c, .bin, etc.) using **Version Control Systems**, along with collaborative development platforms like sourceforge.net, github.com, etc. In the image *Firefox project SCIs files (mozilla-esr128)* you can see an example of the release of the [Firefox source code](https://searchfox.org/mozilla-esr128/source/).

This source code will later be compiled by the maintainers of GNU/Linux distributions (Fedora, Red Hat, Debian, Ubuntu, etc.), performing their own SCM. But unlike the former, GNU/Linux Distributions only work on a single type of SCI: **the package**, where they will insert the program already compiled and/or adapted to their system. You can see in the image *Firefox SCIs packages released by Debian* the [packages released by Debian](https://ftp.debian.org/debian/pool/main/f/firefox/) related to Firefox.

\

As we will see later, this simple fact of **packaging the software** allows to guarantee, in an extremely effective and simple way, the integrity against software changes on the end machines of the different GNU/Linux distributions, thanks to Package Management Systems (PMS).

Architecturally, this converts the package repository into the **Single Source of Truth** (SSoT). Any element not registered and validated in this repository is, for SCM purposes, non-existent or a deviation from the system’s integrity.

\

## Package Management Systems

A [PMS](annex05-glossary.md#term-PMS) (*Package Management System*) is a fundamental tool in software administration, as it facilitates the installation, updating, configuration, and removal of programs in an operating system. These systems are common in software development environments, servers, and GNU/Linux-based operating systems, though they also exist in other environments.

A PMS consists of these three elements:

> 1. **Repository**: It is a centralized store where software packages are saved. Repositories contain the packages along with their metainformation. This metainformation includes a list of dependencies on other packages, required for them to function correctly.
> 2. **Package manager**: Comprises the frontend and the backend.
>    * **Frontend**: It is the interface with which the user interacts. It can be a command line (CLI) or a graphical interface (GUI). The frontend facilitates running commands to search for, install, update, remove, and manage packages, providing a simple way to manage software on the system.
>    * **Backend**: It is the component responsible for the internal logic of the package manager. It handles installing, updating, and removing packages, as well as resolving dependencies. When installing a package, the backend identifies what other packages are required for its operation and ensures that all dependencies are satisfied before completing the installation. In addition to managing software installation, the backend also handles the local database that records the system status—namely, which packages are installed, their versions, and their configurations. This database allows for managing updates, dependencies, and package status on the system.

>      The installation and update process involves:
>      > * **File extraction**: The backend extracts the files from the package and installs them on the system. This includes binaries, libraries, configuration files, and other required components. In some cases, the package may contain scripts that run before or after installing, updating, and/or removing the software.
>      > * **Metainformation**: The package’s metainformation (like dependencies and configurations) is extracted from the package and stored in the backend’s database. This information is crucial for managing updates and ensuring there are no conflicts between installed packages.
> 3. **Package**: It is a file containing the software to be installed, along with all the information about its dependencies and configuration files. A package can have strict dependencies (required to function) or recommended ones (which improve the experience).
\

Well-known examples of PMS are:

> * **APT** (Advanced Packaging Tool): Mainly used in Debian-based GNU/Linux distributions (like Ubuntu, Zorin OS, Linux Mint…). It manages .deb packages and is known for its ease of use.
> * **YUM** (Yellowdog Updater, Modified): Used in distributions like Red Hat, Fedora, or Rocky Linux. YUM is used to handle .rpm packages.
> * **Pacman**: Used in Arch Linux and its derivatives, it manages .pkg.tar.zst packages.
\

PMSs, largely introduced by distributions like [Debian](https://www.debian.org/), have **revolutionized** the way software is distributed, installed, and managed in operating systems.

Before their implementation, installing software on GNU/Linux systems and other computing environments could be a complex and error-prone process, as it required users to manually download and install each necessary component, in addition to managing dependencies and versions independently.

With the arrival of packaging systems, such as Debian’s [Advanced Packaging Tool](https://salsa.debian.org/apt-team/apt) (APT), software management was greatly simplified.

These systems allow software packages to be distributed in a structured and organized manner in centralized repositories, facilitating their download and installation via simple commands. Furthermore, package managers are capable of automatically resolving dependencies, ensuring that all components required for an application to function correctly are installed along with the main software.

One of the great advances of packaging systems was the ability to keep software updated easily. Thanks to **automatic updates**, users can ensure that their applications and operating system are always at the forefront, with the latest features and security patches, without the need for manual intervention.

In addition, PMSs have improved security by offering **verified and digitally signed packages**, which reduces the risk of installing malicious software. They have also enabled better version management, as package managers can handle multiple versions of the same software and ensure compatibility is maintained between different applications and their dependencies.

They have not only facilitated software distribution and installation, but have also optimized system administration, improved security, and increased the efficiency and reliability of GNU/Linux distributions and other package-based systems.

\

GNU/Linux distributions generally perform change control up to the release process, without extending it to the final deployment on computers. However, in organizations with thousands of computers, it is essential to carry traceability, control, and auditing beyond the release, ensuring these practices are also applied during deployment.

This approach guarantees that changes are deployed consistently and in a controlled manner across all end devices, facilitating compliance with internal and external regulations.

Although many GNU/Linux distributions do not integrate deployment within the CCS, specific tools exist, such as migasfree, that allow extending configuration to end machines, ensuring complete traceability and control.

[Ian Murdock](https://en.wikipedia.org/wiki/Ian_Murdock), founder of Debian, highlighted that the great contribution of free software to the industry has been the invention of the packaging system (package, repository, package manager), a system that ensures integrity against changes. This is rightly so, as this system provides two key elements: dependency control via the package manager, and auditing and traceability through queries to the backend database.

A PMS not only optimizes the release and management of changes in configurations or software, but is essential to guarantee traceability, control, and auditing during deployment, especially when managing large or complex environments. This allows for rigorous tracking and efficient management of changes, both in the release process and in its final distribution to servers or end devices.

Thanks to the integration of PMS in migasfree, effective control and traceability are achieved, not only for each SCI, but also for each machine in an IT park, all managed centrally.

\

### Package manager

A package manager is a software application that automates the process of handling packages in the operating system.

Package managers work with software repositories, which are centralized collections of packages and metadata files. These repositories contain information about versions, dependencies, and other characteristics of the available packages.

When installing or updating a package, the package manager interacts with these repositories, downloading the necessary files and creating a local cache file with the updated metadata. This local file contains crucial information about the package name, version, and other details, facilitating updates and efficiently managing changes in the system.

#### Functions

> 1. **Installation, Removal, and Update**: The package manager allows for installing, removing, and updating software packages, managing all necessary dependencies so that the software functions correctly on the system.
> 2. **Dependency Management**: Packages often depend on other packages to function correctly. The package manager automatically resolves these dependencies, ensuring that all necessary libraries and tools are installed alongside the main package, preventing errors and conflicts.
> 3. **Centralized Repository**: Package managers provide easy access to vast collections of libraries and applications through centralized repositories, making it easy to install thousands of programs without searching manually.
> 4. **Version Management**: With a package manager, it is possible to install a specific version of software and update it automatically when necessary. This ensures that the system is always up-to-date and that users can select the version that best fits their needs.
> 5. **Security and Trust**: Package managers use digital signatures to verify the authenticity of packages before they are installed, providing an extra layer of security and reducing the chance of installing malicious software.
> 6. **Automatic Conflict Resolution**: When multiple packages require the same dependencies or versions of a library, the package manager is able to resolve these conflicts automatically, ensuring that the system continues to function correctly without generating inconsistencies.
> 7. **Update Management**: Updating the system is greatly simplified with package managers, allowing all installed packages to be updated with a single command, without manual intervention for each one.
> 8. **Package Search**: Package managers usually include search functions that allow for quickly locating any available software or library in the repositories, saving the user time.
\

#### Operations

Software installation, updating, and removal are fundamental operations in modern operating systems management, essential for ensuring the functionality, stability, and security of environments.

During software **installation**, the package manager not only installs the requested package but also automatically resolves the necessary dependencies. This involves searching for and installing other required packages, managing transitive dependencies (i.e., dependencies of dependencies), and resolving potential version conflicts. Once these dependencies are resolved, the system downloads the packages, installs them, and configures the necessary files on the system.

In the **update** process, the package manager compares installed versions with those available in the repositories to identify those with newer versions. If updates are detected, the manager resolves dependencies again, and if there are no conflicts, downloads the updated packages from the repositories. Subsequently, the system backend uninstalls the old versions and completes the installation of the new versions.

Through **removal**, the package manager facilitates the uninstallation of software in a controlled and safe manner. This includes identifying and removing the specified package, as well as managing related dependencies. If other packages depend on the software to be removed, the manager notifies the user or, depending on configuration, also removes those packages to prevent system inconsistencies. Furthermore, the manager updates internal databases to reflect the changes, ensuring no orphaned files or unnecessary configurations are left that could affect performance or disk space.

In addition to installing software from online repositories, many package managers allow for **installing** packages directly from **local files**. These can be manually downloaded files, such as .deb, .rpm, or .pkg.tar.zst, containing the software to be installed. This operation is particularly useful when internet access is unavailable or when installing a custom version of a package that is not available in the repositories.

In some situations, it may be necessary to **revert an update** and return to a previous version of a package, especially if a new version introduces bugs or incompatibilities. Package managers allow performing a “downgrade” of packages, installing an older version that works correctly with the rest of the system. This operation is useful for maintaining system stability when updates cause unexpected problems.

#### Command Comparison: Frontend vs Backend

To practically illustrate the division of responsibilities between high-level managers (with dependency resolution over repositories) and low-level ones (direct manipulation of package files on disk), the most common operations in the main distribution families are summarized below:

\\begin{landscape}

#### Equivalence of operations in Frontend managers (high level with repositories)

| Operation             | **APT** (Debian / Ubuntu)     | **DNF / YUM** (Fedora / RHEL)   | **ZYpper** (openSUSE)            |
|-----------------------|-------------------------------|---------------------------------|----------------------------------|
| **Update metadata**   | `apt update`                  | `dnf check-update`              | `zypper refresh`                 |
| **Update system**     | `apt upgrade`                 | `dnf upgrade`                   | `zypper update`                  |
| **Install package**   | `apt install <package>`       | `dnf install <package>`         | `zypper install <package>`       |
| **Uninstall package** | `apt remove <package>`        | `dnf remove <package>`          | `zypper remove <package>`        |
| **Search packages**   | `apt search <pattern>`        | `dnf search <pattern>`          | `zypper search <pattern>`        |
| **Query provider**    | `apt-cache madison <package>` | `dnf provides <package>`        | `zypper what-provides <package>` |

#### Equivalence of operations in Backend managers (low level without dependencies)

| Operation                   | **dpkg** (Debian / Ubuntu)   | **RPM** (Red Hat / Fedora / SUSE)   |
|-----------------------------|------------------------------|-------------------------------------|
| **Install local file**      | `dpkg -i <file.deb>`         | `rpm -ivh <file.rpm>`               |
| **Uninstall package**       | `dpkg -r <package>`          | `rpm -e <package>`                  |
| **Search by file**          | `dpkg -S <file>`             | `rpm -qf <file>`                    |
| **List files of a package** | `dpkg -L <package>`          | `rpm -ql <package>`                 |
| **Technical information**   | `dpkg -s <package>`          | `rpm -qi <package>`                 |
| **List installed packages** | `dpkg -l`                    | `rpm -qa`                           |
\\end{landscape}

### Repository

Online repositories are a fundamental part of the package manager ecosystem, functioning as centralized sources from which software packages are downloaded and installed. A repository is essentially an organized collection of packages that can be distributed and managed efficiently.

Package managers use these repositories to access updated versions of software, facilitating the installation, updating, and maintenance of programs on the system.

An online repository is a server or set of servers that stores software packages, usually organized in structured directories according to the operating system and hardware architecture.

These packages are available to be downloaded automatically through a package manager, allowing users to install software without having to manually search for installation files or worry about version compatibility. Repositories are essential for keeping the system up to date and secure, as they typically include the latest versions of software along with security patches.

#### Types of repositories

There are several types of online repositories, which can be classified according to different criteria:

> * **Official repositories**: These are repositories managed and maintained by the developers of the operating system or distributions. These repositories contain software that has been tested and verified to work correctly within that environment. Examples of official repositories are those of Ubuntu, Fedora, or Debian. Their main advantage is that they are well controlled and secured, offering stable and safe versions of packages.
> * **Community repositories**: These are maintained by the community of users and software developers. These repositories contain a wider variety of software, often more experimental or in development.
> * **Private repositories**: Some organizations or companies create private repositories to distribute specific software, such as internal applications or custom tools. These repositories can contain private and custom packages and are accessible only to authorized users.

#### Repository management

Package managers allow for managing the repositories configured on the system. This includes tasks such as:

> * **Adding and removing repositories**: Administrators can add additional repositories to access more packages or remove those that are no longer needed.
> * **Updating repositories**: Package managers allow for updating the lists of packages available in the repositories, ensuring the system has access to the latest versions and security updates.
> * **Prioritizing repositories**: On some systems, administrators can set priorities among repositories. This can be useful when there are multiple sources for the same package, ensuring that the preferred version is installed.

#### Repository structure and protocols

Online repositories generally follow a hierarchical structure in which packages are organized in directories by name, version, architecture, etc. This structure allows for fast and efficient management of the available software. In addition, online repositories use standard protocols to facilitate communication with package managers, the most common being:

> * **HTTP/HTTPS**: Most repositories use these protocols for package transmission, guaranteeing secure and reliable software downloads.
> * **FTP**: Some older or specific repositories use FTP for package distribution, although this protocol is being replaced by more secure options like HTTPS.
> * **File**: For local repositories, the file protocol allows direct access to packages and index files stored on the file system. It is an ideal option for offline environments or where network independence is preferred, and its usage is based on local paths, such as `file:///path/to/your/repository/`.

#### Repository update and maintenance

The constant updating of repositories is crucial to ensure that users have access to the latest versions of software and security patches. Repository maintainers are responsible for uploading new versions of packages, verifying their integrity, and removing obsolete or insecure versions. In addition, repositories usually have quality control systems, such as verifying digital signatures, to ensure that packages are not compromised.

#### Advantages of using online repositories

> * **Ease of access and distribution**: Repositories allow for easy access to software without having to worry about compatibility or searching manually for files.
> * **Security**: Well-managed online repositories offer fast and effective security updates, reducing the risk of vulnerabilities in the system.
> * **Consistency**: By installing software from an official repository, users ensure that software versions and dependencies are compatible with each other, avoiding incompatibility issues.
> * **Community and support**: Community repositories offer access to a wide range of additional software and are often backed by an active community that can provide support and improvements.

#### Disadvantages and considerations

> * **Dependency on repositories**: Users depend on online repositories to obtain software, which can be an inconvenience if the repository is unavailable or does not contain a specific package version.
> * **Security**: If not managed properly, repositories can be an attack vector. It is important to use only trusted repositories and verify digital signatures of packages before installing them.
> * **Software availability**: Not all packages are available in official repositories, which may require adding external repositories or using community repositories, which can be less stable.
\

### The package

In PMS, a package is an organized collection of compressed files that bundles everything needed to install, configure, and run an application or library in the operating system. It acts as a container that encapsulates the files released by a software project, like Firefox for example, along with its dependencies and configurations essential for its proper functioning.

#### Content of a package

> * Essential files:
>   > * Binaries: Precompiled programs ready to run.
>   > * Documentation: Manuals or guides related to the software.
>   > * Configurations: Files that define the initial behavior of the software.
> * Detailed metainformation: Packages include rich metainformation, such as:
>   > * The program author and the packager.
>   > * The software version and the Version Control System (VCS) version.
>   > * The compatible architecture.
>   > * The project repository address.
>   > * Dates and details of the packaging process.
>   > * Short and detailed descriptions of the package and its content.
>   > * Dependencies on additional packages required for the software to function.
> * Scripts: Packages typically include code that runs at specific stages:
>   > * Pre-installation and post-installation: To configure the environment or make adjustments before and after installing the package.
>   > * Pre-upgrade and post-upgrade: To prepare the system before an upgrade and clean up or configure after it.
>   > * Pre-removal and post-removal: To revert configurations or clean up residues when uninstalling.
\

#### Release

In environments like GNU/Linux, once a maintainer creates a package, they publish or **release** it to public repositories managed by the corresponding distribution. Repositories act as centralized stores from which users can download and install software safely and efficiently.

The maintainer of a package is the person or team responsible for:

> * **Preparing the package**: Compiling the software, including required dependencies and metadata, and verifying that it complies with the distribution standards.
> * **Managing updates**: Keeping the package updated with new versions of the software, including bug fixes and security patches.
> * **Integrating the package into the system**: Ensuring that it functions correctly on the specific distribution, resolving dependency conflicts and adapting configurations if necessary.
> * **Monitoring and resolving problems**: Attending to bug reports and making adjustments according to user needs or changes in the original software.

The maintainer collaborates closely with the distribution’s Change Control System (CCS).

The existence of public repositories ensures that users have access to:

> * Reliable and verified versions of the software.
> * Regular updates with bug fixes and security improvements.
> * Automated integration to resolve dependencies.

The package manager uses this information to:

> * Install, update, or uninstall software efficiently.
> * Manage dependencies automatically, ensuring that required components are available.
> * Provide a history and centralized control over installed applications and libraries.

The package, in short, is the fundamental unit that allows PMS to operate in a structured, efficient, and secure manner, reducing manual efforts and guaranteeing system integrity.

> #### NOTE
> If you are used to installing programs through the typical “./configure, make, install”, you must be aware that you are breaking integrity against changes, as the backend database is not updated with this procedure. Anything other than installing programs through the package manager or the backend breaks change integrity.
\

### Multiple package managers

The coexistence of two package managers in the same Linux distribution, such as APT and Snap in the case of Ubuntu, has significant implications in the context of SCM.

It requires documenting clear policies on their use to ensure consistency and replicability, integrating automation tools that handle both systems despite their complexity, and considering long-term compatibility, as prioritizing one may leave the other obsolete. Furthermore, although Snap improves security through isolation, coexistence with APT expands the attack surface, requiring active vigilance on updates and vulnerabilities.

This coexistence introduces an additional layer of complexity to SCM:

> * **Application duplication**: The same application may be available in both formats (e.g., Firefox in APT and Snap), generating confusion about which to install.
> * **Configuration synchronization**: Applications managed by different systems may store configurations in different places, complicating centralized administration.

Systems like Snap, being more autonomous, can cause inconsistencies:

> * Snap packages do not respect global system configurations (such as GTK themes or environment variables).
> * Performance issues: Snaps tend to be slower to start due to isolation and the need to mount their filesystems.

In conclusion, having two package managers in a Linux distribution can offer flexibility and support for a wider range of applications, but it also introduces significant challenges in terms of complexity, consistency, and management. From the SCM perspective, it is essential to:

> * Adopt clear standards on the use of each manager.
> * Carefully automate and supervise software updates and configuration.
> * Evaluate the long-term impact of maintaining this duality.

For all these reasons, it is advised to use a single package manager to simplify administration and reduce conflicts.

\

### Windows

It is necessary to clarify the difference between a PMS (*Package Management System*) and package managers for Windows, such as Winget, Chocolatey, or Scoop. Although both PMS and these tools facilitate the installation and management of software, their scope and approach are different. Traditional PMS, such as APT or YUM, are designed to manage the entire software ecosystem **at the operating system level**, including applications, shared libraries, and dependencies. On the other hand, package managers for Windows are mainly focused on installing, updating, and managing **user applications**, although they can also handle dependencies to a lesser extent.

In the Windows environment, due to its heterogeneous ecosystem of installation formats (MSI, EXE, APPX, MSIX, ClickOnce, ZIP/Portable, scripts, etc.), these tools act as a layer that simplifies the process, which often leads to considering them as “installer managers.” However, this does not disqualify them as package managers, as they perform a similar function adapted to the particularities of Windows.

A key feature in traditional package management systems like those used in GNU/Linux is **non-interactivity** with the user, as it allows for fully automating installations, updates, and uninstallations without manual intervention. This is especially useful in enterprise environments and on servers where consistency and efficiency are required.

However, in Windows, achieving this level of automation faces several challenges. Many applications in Windows are designed with graphical installers (such as MSI or EXE), which frequently require user interaction to accept terms, configure options, or provide information during the process. Although package managers like Chocolatey, Winget, or Scoop attempt to minimize this dependency, they do not always manage to avoid interactive prompts, especially when the underlying installers are not designed to operate completely silently. Furthermore, issues like the need for system reboots or administrator permissions (UAC) can interrupt automated flows, complicating their implementation even more compared to GNU/Linux systems, where design philosophy prioritizes non-interactivity from its foundations.

From the software architecture point of view, the key difference lies in the management of **shared dependencies**. While a PMS in Linux manages a global graph of libraries (minimizing redundancy and facilitating global security audits), Windows installers tend to be self-contained, bringing their own versions of the required libraries. This resolves local conflicts (“DLL Hell”) but fragments the system configuration, hindering a centralized and consistent SCM.

And although tools like Chocolatey and Winget provide configurations to run “silent” or “unattended” installations, the experience varies by application and the specific installer. This underscores the fundamental difference in software design between the Windows and GNU/Linux ecosystems, where package managers are more integrated with the operating system and its ecosystem of software preconfigured to function without user intervention.

\

## Continuous Integration and Continuous Deployment

**Continuous Integration** (CI) is a software engineering practice that consists of making **automatic integrations** of a project as often as possible to detect failures as early as possible. By integration, we mean the compilation and test execution of a project.

**Continuous Deployment** (CD) is the practice of releasing software reliably and automatically at any time, reducing the costs, time, and risks associated with release versions through more frequent and **automated releases and deployments**. This allows the software to always be ready to be deployed to production, without manual intervention, guaranteeing a continuous and secure flow of updates.

**CI/CD is conceived as an infinite loop** that fosters iterative development and constant improvement. This cycle represents an agile approach to creating, delivering, and maintaining software, ensuring that each change is integrated, tested, and deployed without interruptions. Instead of being a linear process, CI/CD establishes a continuous feedback loop, where each phase not only depends on the previous one, but also informs and improves the next ones. This uninterrupted flow ensures that teams can respond quickly to changes, identify issues at early stages, and maintain quality in every iteration.

\

### Phases of CI/CD

1. **Plan**

   It all starts with a planning phase in which teams define goals, identify requirements, and prioritize tasks. In this stage, user stories are created, sprints are assigned, and technical strategies are discussed. Planning establishes the foundation for development by ensuring that everyone involved is aligned with the project vision.
2. **Code**

   Developers write code based on the defined requirements. Using version control (such as Git), branches are created to ensure each change is isolated and managed. This phase also includes code reviews to guarantee consistency, quality, and compliance with standards.
3. **Build**

   In this stage, code is compiled and packaged in an executable or deployable format. Automation processes verify that all components work together without conflicts. The goal is to ensure that the software can be implemented in any environment without errors.
4. **Test**

   The testing phase verifies that the software functions as expected. This includes unit, integration, regression, and acceptance testing. The results allow for identifying errors and ensuring that changes do not introduce problems into the existing system. This stage is key to guaranteeing stability before moving forward.
5. **Release**

   Once the software has passed testing, it is packaged and tagged for release. In this phase, teams decide which software versions will be available for specific users or environments, ensuring the release is safe and controlled.
6. **Deploy**

   Here, software is implemented in production environments. Using automation tools, such as CI/CD pipelines, changes are deployed without interruptions. In many cases, continuous deployment is used to deliver new versions as soon as they are ready.
7. **Operate**

   Once in production, the software enters active operation. This includes environment configuration and resource management to ensure the application runs as expected, handling the load and providing access to end users.
8. **Monitor**

   Finally, the software is monitored to measure performance, identify issues, and collect data on actual usage. Monitoring and logging tools provide feedback that helps teams correct bugs, optimize functions, and plan new improvements, closing the infinite loop cycle.

   In a mature SCM environment, monitoring acts as an **automated and continuous audit**, verifying in real time that the “real state” of production systems matches exactly the “registered state” in the configuration.

This iterative approach not only ensures fast and reliable deliveries, but also allows teams to adapt to changing needs and maintain a constant standard of quality.

\

## Summary

In this chapter, you have seen that the package is the piece that is managed, that the change request structures the process, and that migasfree leverages native packaging to govern an entire fleet without reinventing the wheel. This order facilitates teamwork and reduces risks, making development more agile and efficient.

**Change** is **inevitable and desirable**.

Software Configuration Management: **SCM is responsible for controlling and tracking changes** in software and its environment. Its scope covers all Software Configuration Items (SCIs).

**Integrity** ensures traceable, authorized, and consistent changes throughout all phases of the software lifecycle.

The Change Control System: **CCS is part of SCM**, being the set of processes, policies, and tools used **to manage changes in a controlled manner**, in a continuous cycle of requests, changes, and releases. Its scope is limited to one or several SCIs, but not the entirety of them as SCM does.

**GNU/Linux** distributions only work on a **single type of SCI**: **the package**. They use **Package Management Systems** (PMS) to **deploy** changes in software, **ensuring control, traceability, and integrity**.

**migasfree uses the PMS** to deliver applications and configurations in a precise, centralized, and automated manner, greatly facilitating operating system administration. The use of migasfree guarantees SCM integrity also in the deployment phase.

Continuous Integration and Continuous Deployment: **CI/CD focuses on the automation** of development and delivery processes, ensuring that software is integrated and deployed continuously.

# Centralized Management

> > In everything that surrounds us and in everything that moves us, we must observe that chance plays a part.

In the previous chapter, we discussed SCM and how GNU/Linux distributions use the package management system to guarantee integrity against change.

If you have a home desktop computer, all the changes produced and released by various projects—and packaged and released by your GNU/Linux distribution—will be conveniently installed simply by commanding the package manager to update your system.

However, in an organization where desktops need to be managed, this is not enough; let us see why.

\

## Customization

The first major challenge you will face is customization.

Imagine you have to migrate and manage 1,000 machines to GNU/Linux, and you have an NTP service on your network requiring all your desktops to keep their time synchronized with it.

You are going to have to customize the NTP client on all your desktops.

A rudimentary method often used is to install a GNU/Linux distribution on a computer from a DVD, edit the NTP client configuration file, and configure the IP (or DNS name) of the server hosting the NTP service. Afterwards, you can create a hard drive image using a cloning system like [Clonezilla](http://clonezilla.org/) and clone the machines one by one using that image.

With this method, the initial customization resides within that image, but let us keep imagining…

One day, halfway through the migration, you receive an email reading:

> Alberto: The NTP service will be decommissioned as of the 10th. In its place we will have a new service called QueHoraEs, which is much better because…

At this point, you will already be thinking about the 400 machines you have migrated and putting your hands to your head, because it is obvious that this customization method is inadequate.

> #### NOTE
> Initial customization is very easy to perform, but a change in customization can happen at any time, and you must be prepared to handle it.
\

### Systems Management Systems

Fortunately, there are tools known as **Systems Management Systems** ([Systems Management Systems](https://en.wikipedia.org/wiki/List_of_systems_management_systems)) that can assist us in desktop administration.

Some of these Systems Management Systems focus on querying the state of machines, such as [Nagios](https://www.nagios.org/), while others allow automating tasks by running code on machines centrally, such as [Zenworks](https://en.wikipedia.org/wiki/ZENworks), [Landscape](https://ubuntu.com/landscape), [Chef](https://www.chef.io/products/chef-infra), [Puppet](https://www.puppet.com/), [CFEngine](https://cfengine.com/), [Ansible](https://www.ansible.com/).

Systems Management Systems are heavily influenced by initiatives carried out in telecommunications network management systems, and are capable of performing one or a set of the following tasks:

> - Hardware inventory.
> - Server availability monitoring and metrics.
> - Software inventory and installation.
> - Antivirus and anti-malware management.
> - User activity monitoring.
> - System capacity monitoring.
> - Security management.
> - Storage management.
> - Network utilization and capacity monitoring.

We can classify these tasks according to the ISO network management model [FCAPS](https://en.wikipedia.org/wiki/FCAPS) (*Fault, Configuration, Accounting, Performance, Security*). It is an academic reference framework: you do not need to memorize its categories to work with migasfree, but it will help you understand where configuration management fits within the overall management of a network.

> #### NOTE
> In migasfree, in terms of FCAPS, we have Fault, Configuration, and Accounting capabilities.

A typical operating example of a Systems Management System incorporating *Configuration* tasks would use a language specifying what state machines should reach, rather than how to get to that state. In our case, it would look something like this:

* ensure package ntp-client is uninstalled,
* ensure package quehoraes-client is installed,
* ensure that the quehoraes-client configuration file is identical to the one on the server.

Periodically, clients connect to the server to retrieve this code, which is executed by the Systems Management System interpreter installed on the client.

In this context, **migasfree** provides an upper layer of **governance**, ensuring **auditing** (who requested the change and when), **version control** (which exact change was applied), and **traceability** (what the outcome of the operation was).

> #### NOTE
> **The Declarative Convergence Model**

> Unlike traditional scripts that execute commands sequentially, migasfree operates under a **declarative model**. You do not have to define *how* to change the system, but simply *what* its **Desired State** should be.

> migasfree-client handles **convergence**: it downloads metadata from the server, compares it with the machine’s **Current State**, calculates the difference (the **Delta**), and does whatever is necessary to bring both states into alignment. This guarantees **idempotence**: no matter how many times the machine synchronizes, the result will always be identical and completely predictable.
\

### Packaging Customization

In AZLinux we use another approach: we always package customization.

To execute these technical operations, you can include your own scripts (in Bash, Python, etc.) or **Ansible** *playbooks* inside a package. By doing so, every execution is centrally logged by the server, tying the state of the machine to the package database. This ensures system integrity, overcoming the limitations of tools that maintain standalone control inventories.

For the “QueHoraEs” client, we would create the package azl-quehoraes-client  with the following information:

* Dependencies: quehoraes-client
* Obsoletes: ntp-client
* In the post-installation script we would write the following code:
  > In the QueHoraEs client configuration file, replace the value of the “server=” entry with the IP address of the QueHoraEs server

*  In AZLinux we use the “azl-” prefix followed by the name of the package we want to customize, facilitating searches and allowing us to filter between our organization’s packages and the rest.

Done! With this, the integrity of the customization against change is guaranteed, leveraging the integrity provided by our GNU/Linux distribution’s packaging system.

Once our customization is packaged, making any subsequent change to it becomes relatively straightforward. However, creating a package from scratch to customize a GNU/Linux distribution is not so simple—not so much because of package creation itself, but because customization requires sufficient knowledge of the GNU/Linux system and of the application being customized.

> #### NOTE
> Packaging customization ensures system integrity against change.

> Notice that no Systems Management System is required to install this customization. You only need the Package Manager, and that is always available on any GNU/Linux distribution.
\

### Customization Levels

Software applications typically incorporate two levels of customization:

> * **User-level customization**: Individual configurations adapted to each user’s specific preferences or needs.
> * **Operating system-level customization**: General configurations applied to all users on the system.

Generally, user customization takes precedence over system customization, unless the latter is defined as mandatory. It is crucial to verify whether the application allows system-level configurations, as these constitute the initial baseline that must be established.

When an application only supports user-level customization, or if specific configurations must be applied to each user, preferences will need to be adjusted individually.

Understanding an application’s customization capabilities is essential for planning its configuration efficiently. Furthermore, it is important to consider an additional level of customization:

> * **Organizational-level configuration**: This approach establishes standards and guidelines that align individual and system configurations with the overall goals of the enterprise or institution.

Organizational configuration promotes consistency, improves management efficiency, and facilitates compliance with internal policies or external regulations. This is especially relevant in large or complex environments, where ensuring uniformity across certain customization aspects is essential. Consistent implementation also contributes to smooth operations and optimizes technical support.

migasfree simplifies organizational configuration management by centralizing, standardizing, and automating its distribution, ensuring uniform and efficient deployment aligned with institutional objectives.

\

An example of organizational configuration would be a package setting LibreOffice identity details according to a **defined corporate policy**, preventing users from modifying this information.

\

## Release Management

This is the second major challenge you will have to deal with.

On one hand, you must decouple from your GNU/Linux distribution’s public repositories, for the simple reason that you cannot allow your GNU/Linux distribution to control the changes installed on your machines instead of your organization.

Can you imagine what would have happened in AZLinux when openSUSE replaced OpenOffice with LibreOffice? When users turned on their computers at 8:00 AM, the upgrade to LibreOffice would start automatically, potentially causing many incidents. Would everything work? Is it not better to test LibreOffice in your organization before deploying it to all your machines?

Having the ability to roll back a change deemed undesirable is important.

You must decide for yourself what software your users should have and, therefore, you must configure package managers against your own package repositories and manage them somehow.

Additionally, it is advisable to be able to schedule who receives these changes and when.

Imagine again the example of replacing OpenOffice with LibreOffice. We would be talking about an upgrade of nearly 500 MB per computer, which, multiplied by all machines across an organization, could generate substantial network traffic.

An advantage of planned releases is that it allows distributing changes gradually, so that if bugs arise, only a few machines are initially affected, giving you more breathing room to resolve any incident.

For all these reasons, and because standard distribution repositories lack release scheduling mechanisms, we decided to develop migasfree, extending the concept of a package repository into a deployment: a dynamic, schedulable package repository.

### Configuration is not a script; it is a live package

Traditionally, automation relies on sequential *scripts* or *playbooks*. migasfree breaks this paradigm by using standard packaging systems (deb/rpm) to express configurations. By treating each adjustment as a package, we shift the burden of state management from the administrator’s *script* to the robust logic of the operating system package manager. This approach guarantees state convergence through version control, digital signatures, and native *rollback* capabilities. By encapsulating configuration into self-contained units, we achieve superior governance: we no longer rely on the scripting expertise of a single programmer, but on mature, auditable software engineering processes.

\

## migasfree Deployment

A migasfree deployment is simply a standard repository combined with the ability to centrally specify who accesses that repository and when.

Let us see how migasfree behaves regarding repositories:

> 1. The changes to be released are packaged and uploaded to a migasfree server.
> 2. A deployment is created with the uploaded packages, specifying to whom (user + computer attributes) and when those changes should be applied.
> 3. The migasfree server creates a physical repository (identical to that of any GNU/Linux distribution) containing those packages, using standard repository creation tools (createrepo for RPM packaging or apt-ftparchive for Debian packaging).
> 4. When a migasfree client connects to the server, it sends its attributes.
> 5. The server queries deployments to determine, based on those sent attributes, the list of physical repositories available to the client, and returns them.
> 6. The migasfree client configures the list of physical repositories received from the server in the Package Manager.
> 7. Next, the migasfree client instructs the Package Manager to remove, install, and update packages from the physical repositories.

## Organic Scalability: The Attribute as DNA

In migasfree, an [attribute](annex05-glossary.md#term-Atributo) is not merely a tag or a database field; it is the **DNA** defining each machine’s identity and behavior. This concept transforms fleet management from a static administrative chore into an **organic scalability** process.

Traditionally, scalability is understood as the ability to add more nodes to a system. However, in a complex environment, the true challenge is not *how many* nodes you have, but *what* each one should be at any given moment.

Through attributes (hardware, physical location, VLAN, department, etc.), infrastructure behaves like a living organism:

* **Dynamic Identity**: The system self-defines in real time. If you move a computer from one office to another, its attributes change, and migasfree adjusts its configuration automatically.
* **Autonomous Remediation**: The system reacts to changes in its own state. If new hardware is detected, the system does not just add software; it detects attribute changes, automatically removes obsolete drivers, and installs new ones.
* **Rule-Based Management**: Picture migasfree as a massive spreadsheet: attributes are data, and deployments are rules. When data changes, rules apply instantly, allowing the organization to grow without constant manual intervention.

\

## CCS in Your Organization

In the previous chapter, we saw the CCS process across open-source projects as well as GNU/Linux distributions.

This process should also be adopted in your organization, as illustrated in: *Closed-Loop Governance with migasfree*.

1. Closed-Loop Governance with migasfree
2. The **User Support Center (CAU)** serves as the central hub where user requests arrive, registering change requests and forwarding them to the technical team.
3. The **Technical Team** analyzes, develops, and packages solutions in a local development environment, ensuring compliance with software engineering standards.

   Through **migasfree deployments**, packages are uploaded and scheduled for progressive distribution to desktops and servers, ensuring controlled and predictable adoption.
4. **Auditing** and **monitoring** close the loop. A mature change control system does not end with package release. True governance requires a continuous **feedback loop** to verify in real time whether changes applied successfully or if configuration drift exists. This cycle guarantees that **State Accounting** is a reality rather than merely documentation intent.

> \

In AZLinux, we can distinguish between these two types of change requests:

* **Application updates**. If we receive a request to update Mozilla Firefox, for example, we download the desired version from the distribution repositories. We test it in the lab, recording any relevant information in the change request. Finally, if everything is sound, packages are released through a migasfree deployment, scheduling their distribution (see A in: *Software Configuration Management Processes*).
* **Application customization**. This occurs when a change request arrives to add a synonym search engine to Mozilla Firefox, for instance. We then add the code to install that search engine into our own AZLinux package (azl-firefox) and release it in a migasfree deployment, scheduling its distribution (see B in: *Change Control System Processes*).

\

The image *AZLinux 22 Package Structure* illustrates how packages developed in AZLinux are organized. Although extensive at first glance, this structure is the result of years of gradual evolution: in 2008 we started with a single package in AZLinux 1, and since then we have expanded and reorganized it to improve decoupling and optimize dependencies among our packages.

\

### CI/CD

At the end of the previous chapter, we explored a general introduction to CI/CD. Now, I invite you to delve into its practical application in the context of migasfree.

> #### NOTE
> If you have never worked with Git, GitLab, Docker, CI/CD… do not worry. When AZLinux and migasfree started, we did not use any of these technologies; step by step, we learned and incorporated them into our operations. They are not strictly necessary, but as you learn and adopt them, you will witness the tremendous advantages they provide.

To implement **changes**, it is highly recommended to **automate** at least:

1. Package **building**.
2. Package **uploading** to the migasfree server.
3. Package **deployment**.

If you maintain a single migasfree project, it may seem excessive, but once you have two or more—plus many packages to maintain—this automation becomes essential.

> #### NOTE
> On AZLinux desktops, we do not automate migasfree deployment creation; we choose to perform it manually due to the wide variety of scenarios encountered.

> However, for servers we do automate package deployment thanks to CI/CD. We maintain a migasfree deployment for each package and project, updated according to our needs via the migasfree API.
\

In AZLinux, every package is maintained centrally through a [GitLab](https://github.com/gitlabhq/gitlabhq) project. Each of these projects contains a .gitlab-ci.yml file where we **automate** change activities.

A single GitLab project typically serves multiple migasfree projects, such as (AZLinux-20, AZLinux-22, AZLinux-24…).

Below is an example snippet from one of these .gitlab-ci.yml files.

> ```yaml
> # File .gitlab-ci.yml
> # ===================

> variables:
>    _USER: "builduser"
>    _PATH: /home/$_USER/$CI_PROJECT_NAME

> stages:
>    - build
>    - upload

> # AZLinux-22
> # ==========
> build-job-azlinux22:
>    image: registry.acme.com:5000/azlinux22:dev
>    stage: build
>    script:
>       - useradd -m $_USER
>       - mkdir -p $_PATH
>       - mv * $_PATH
>       - pushd $_PATH
>       - su -c "/usr/bin/debuild --no-tgz-check -us -uc" $_USER
>       - popd
>       - mv /home/$_USER/*.deb .
>    artifacts:
>       expire_in: 1 days
>       paths:
>             - ./*.deb
>    only:
>       - tags

> upload-job-azlinux22:
>    image: registry.acme.com:5000/azlinux22:dev
>    stage: upload
>    script:
>       - MIGASFREE_PACKAGER_PROJECT=AZL-22 migasfree-upload -f *.deb
>    dependencies:
>       - build-job-azlinux22
>    only:
>       - tags

> # AZLinux-24
> # ==========
> build-job-azlinux24:
>    image: registry.acme.com:5000/azlinux24:dev
>    stage: build
>    script:
>       - useradd -m $_USER
>       - mkdir -p $_PATH
>       - mv * $_PATH
>       - pushd $_PATH
>       - su -c "/usr/bin/debuild --no-tgz-check -us -uc" $_USER
>       - popd
>       - mv /home/$_USER/*.deb .
>    artifacts:
>       expire_in: 1 days
>       paths:
>             - ./*.deb
>    only:
>       - tags

> upload-job-azlinux24:
>    image: registry.acme.com:5000/azlinux24:dev
>    stage: upload
>    script:
>       - MIGASFREE_PACKAGER_PROJECT=AZL-24 migasfree-upload -f *.deb
>    dependencies:
>       - build-job-azlinux24
>    only:
>       - tags
> ```

This example could represent an AZLinux package. Notice that it consists of two **stages**:

* **build**: In this stage, the package is built inside a Docker container using the specified **image** for each of the migasfree projects AZL-22 and AZL-24.
* **upload**: In this stage, newly built packages (artifacts) are uploaded to the migasfree server, also using a container. Each will be uploaded to its corresponding migasfree project.

Notice that each **stage** has its own **jobs**.

Observe how only: -tags specifies that each job executes only when the **project is tagged**.

Pay attention to how upload-job-azlinux22 depends on build-job-azlinux22 thanks to dependencies: - build-job-azlinux22, just as with azlinux24.

And what about the **azlinux22:dev** and **azlinux24:dev** images? Well, they are basically Docker images based on the base distribution of each of our migasfree projects, where we simply added the migasfree client plus the necessary tools for building packages.

> ```Dockerfile
> # File: Dockerfile (azlinux22:dev)

> FROM ubuntu:jammy

> ENV DEBIAN_FRONTEND "noninteractive"
> ENV USER "root"

> RUN apt-get update \
>    && apt-get install -y devscripts gcc build-essential debhelper python3-stdeb python3-distro dh-python git ca-certificates python3-netifaces wget \
>    && ln -s /usr/bin/python3 /usr/bin/python \
>    && update-ca-certificates \
>    && wget http://$MIGASFREE_CLIENT_SERVER/public/AZL-22/STORES/thirds/migasfree-client_4.20-1_all.deb \
>    && dpkg -i migasfree-client_*_all.deb || : \
>    && apt-get -y -f install \
>    && rm -rf /var/lib/apt/lists/*
> ```

> #### NOTE
> In GitLab’s Settings > CI/CD > Variables, the variables MIGASFREE_CLIENT_SERVER, MIGASFREE_PACKAGER_USER, and MIGASFREE_PACKAGER_PASSWORD must be configured at the group or project level.

In summary, with CI/CD properly configured, the developer handling the change can focus solely on modifying package files and tagging them with a new version. The rest of the process runs completely automatically.

\

### Tools

The primary tools we currently use in each activity are:

* In change requests:
  > - Project manager: [Redmine](http://www.redmine.org/)

* In development:
  > - IDE: [VSCodium](https://vscodium.com/)
  > - Version Control System: [GitLab](https://github.com/gitlabhq/gitlabhq)
  > - Lightweight virtualization: [Docker](https://www.docker.com/)
  > - Project manager: [Redmine](http://www.redmine.org/)

* In release:
  > - Systems manager: [migasfree](http://migasfree.org)
  > - Project manager: [Redmine](http://www.redmine.org/)

> #### NOTE
> migasfree allows us to centrally query the status not only of the migasfree server, but also of every computer registered with it, making it an ideal tool for auditing both software and hardware.
\

## Technical Specialization

The implementation of Software Configuration Management (SCM) at the User Support Center (CAU) of Zaragoza City Council significantly transformed the technical team dynamics, promoting specialization that improved overall process efficiency.

On one hand, technicians responsible for implementing changes focused on mastering the tools, processes, and methodologies needed to apply system modifications accurately and in a controlled manner, while gaining deeper knowledge of the underlying operating system. On the other hand, the rest of the technical team specialized in identifying, diagnosing, and documenting issues, as well as managing change requests. This division of responsibilities enabled closer focus at every stage, improving both requirement detection and solution quality.

This specialization was not planned a priori, but emerged naturally and progressively as we gained experience and refined processes. Overall, this natural evolution not only increased productivity, but also fostered a more collaborative, results-oriented work environment.

Experience proves that a clear definition of roles, combined with continuous learning, is key to optimizing change management in complex systems.

\

## Benefits of SCM

Implementing an SCM system within an organization provides advantages for both the technical team and each individual administrator:

* **Traceability and auditing**: Improves tracking of changes (who made them and why), increasing transparency, facilitating audits, and ensuring compliance in regulated sectors.
* **Version control**: Enables version tracking, simple rollbacks, and error minimization.
* **Reduction of errors and conflicts**: Establishes workflows for approved changes and prevents incompatible configurations, also reducing stress from unforeseen failures.
* **Efficiency and productivity**: Centralizes codebase management, reduces redundancy, improves communication, and enables handling more projects concurrently with less effort.
* **Software quality improvement**: Enforces standards through code reviews, testing, and pre-deployment validation.
* **Process automation**: Simplifies compilation, testing, and deployments, accelerating deliveries and freeing time for strategic tasks.
* **Rapid incident response**: Facilitates diagnosing and resolving incidents, minimizing downtime.
* **Scalability, security, and cost control**: Adapts systems to new demands, controls configuration access, and optimizes resources, reducing costs associated with errors and manual tasks.
* **Professional growth**: Develops highly valued skills in automation, CI/CD, and DevOps, simplifying audit reporting and documentation.

Conclusion: SCM improves software quality, optimizes internal workflows, and positions administrators as more efficient, dependable, and competitive professionals.

In the next chapter, you will discover the features that make migasfree the ideal tool to put everything you have learned into practice: its history, capabilities, and the philosophy behind how it automates configuration management.

# Features

> > Things are not said, they are done, because by doing them, they say themselves.

## The birth of migasfree

In 2005, all political groups in the Zaragoza City Council unanimously agreed, in a municipal government plenary session, to support policies for the use of Free Software, and specifically, to promote Free Software programs in the municipal employee’s desktop environment. The Directorate-General for Science and Technology assumed, initiated, and promoted this important challenge. 

*  Eduardo Romero Moreno, [Free Software Desktop Migration](http://www.zaragoza.es/contenidos/azlinux/migracionescritoriosl.pdf), 2011

This project was planned in three phases:

* **First phase**: Migrate to applications that had a low impact on users and technicians in the current Operating System (at that time, Microsoft Windows XP).
* **Second phase**: Replace the office suite Microsoft Office 97 with the free suite OpenOffice.
* **Third phase**: Replace the Windows XP OS with a Linux-based operating system. This phase began in 2008.

To start the third phase, the first prototypes of what would become the first version of **AZLinux**  had to be built. In these prototypes, customization was performed manually on a machine whose hard drive image served to clone it onto other machines and perform the relevant tests.

*  Pronounced “acetalinux”. It stands for Zaragoza City Council Linux.

At that time, we learned to package and began introducing our customizations into our own packages. The advantage over manual customization was very significant.

With the first real migrations, the need to update our packages arose. After testing *Zenworks for Linux* without success, we decided to create our own package repositories. We wanted to emulate what we were already doing with XP desktops. That is, distributing software based on the Organizational Unit to which a user belonged in our LDAP. With a bit of *Bash scripting*, in May 2009, we implemented what would be dynamic repositories configured on the client depending on the context.

This was undoubtedly a great idea, but the management of these dynamic repositories was manual and very error-prone.

The management of these dynamic repositories fell to me, so I decided to simplify the process and immediately create the first *prototype of migasfree* . In just two weeks of programming, during my non-working hours, I developed a basic prototype that I presented to my colleagues and which was put into production in June 2009.

> #### NOTE
> In 2022, 80% of the 5,000 desktops of municipal workers in the Zaragoza City Council were GNU/Linux. Mission accomplished!
*  It is worth noting that the author of software is the person who develops it, regardless of the context in which the program is used. In the specific case of programs created outside working hours and without using company resources, authorship and ownership of the software belong to the author, not to the company for which they work.
\

## Versions

The first prototype was only compatible with RPM packaging and the YUM package manager, and the bash code executed on the client was generated on the server.

After using migasfree in production for a while, we realized it could be a useful system for other organizations. My colleagues gave me the necessary push to make the code public. Thus, during the summer of 2009, I organized the menus, optimized the code, and adapted migasfree to be compatible with different operating system versions and package managers. The project was [published](https://github.com/migasfree/migasfree) on [GitHub](https://github.com/) in April 2010 and named “migasfree with fried eggs”, because according to my colleagues, the logo looked like a fried egg. What do they know about Art!

In November 2011, Jose Antonio Chavarría, developer of AZLinux, rewrote and published the [migasfree client](https://github.com/migasfree/migasfree-client). In addition, he made significant changes to the server structure, which led us to define an API to establish communication between the client and the server. To strengthen system security, we incorporated the use of asymmetric keys. This new version was named “migasfree no trans”, in reference to a more refined and cleaner code, something I interpret with humor and as a way of recognizing my own limitations.

Little by little, we added new features to the system, and by early 2013, Jose Antonio Chavarría changed the navigation and appearance of the server. This new version was called “migasfree with chocolate”.

In February 2014, we released version 4 of the server (*migasfree grape edition*). This version uses [bootstrap](http://getbootstrap.com/) to provide the application with a web design adaptable to different devices. In addition, it incorporates various improvements of all kinds.

In 2015, we joined a disruptive wave: [docker](https://es.wikipedia.org/wiki/Docker_(software)). This freed us from having to fight with dependencies of the components we used on the server and from having to publish the packages we generated for different GNU/Linux distributions (we use component versions that had not yet been released, which created real headaches).

With *docker*, we managed to place the server and its dependencies in a virtual container (a Debian one) that could run on any GNU/Linux server. This gave us the flexibility and portability to run the server very easily, both on physical hardware and in the cloud.

Version 4 has been active for the longest time, but while it was in force, Jose Antonio Chavarría and I were imagining and working on what would become [suite version 5](https://migasfree.org/blog/2015/2015-04-10-nullius-in-verba.html).

For version 5, Jose Antonio focused on separating the migasfree administration console from the backend services by expanding and improving the REST API, which was functional in v4 but merely experimental. He made a first attempt at an [administration console](https://www.youtube.com/watch?v=3C4axcxuLXg) with Nuxt, but soon discovered Quasar, a framework for Vue, so he started over, seeing how much work it would save. With what he learned, it was time for [migasfree-play](https://youtu.be/uon6ScXdbPM), which he also developed with Vue and Quasar. He also rewrote the [client](https://www.youtube.com/watch?v=v35cWLoEKII), atomizing the calls to the server API, which allows for developing other specialized clients in the future in a simple way.

As for the backend services, the change has been profound. There are improvements in the database structure (packages now have their own entity) and some features have been added, but without a doubt, the deepest change experienced has been the separation of components: it has gone from using only two docker containers (database and server) in v4 to more than ten (proxy, console, public, pms-apt, pms-yum, pms-pacman, pms-wpt, core, beat, worker, datastore, datashare).

While José Antonio dedicated himself to coding, I focused on configuring and optimizing all these containers using Swarm. The set goal was that an administrator, even with basic knowledge of Docker and Swarm, could easily deploy and maintain a migasfree server. Furthermore, we sought to ensure the ability to scale easily, leveraging Swarm to deploy multiple instances of components across different nodes in the cluster.

During this period, another technological hurricane hit us all: **generative artificial intelligence**.

Although we initially developed a conventional AI assistant for migasfree, we soon discarded it upon discovering the potential of the **Model Context Protocol (MCP)**. We decided to create our own MCP server, specifically designed to provide language models with a deep understanding of the ecosystem. This server not only queries the database for real-time information from the machines, but also provides direct access to technical documentation, database schemas, the API, and the complete architecture.

This integration represented an unprecedented qualitative leap. It allowed us to drastically refine existing code and bring to life new projects, such as **migasfree-agent**, whose development would have been simply unreachable without the strategic support of AI.

After this intense cycle of innovation and redesign, the first beta versions of **migasfree 5.0** saw the light in 2025, consolidating with the release of stable versions throughout 2026.

### From v4 to v5: An evolutionary leap

If you have previously worked with version 4 of migasfree, making the leap to version 5 will present you with a completely renovated technological landscape. It is not a simple facelift; it is a deep reconstruction designed to face the challenges of modern administration and scalability.

To make sure you don’t get lost in the transition, here is a quick map of the most consequential changes between both versions:

* **Native support for Golden Images**: v5 embraces the concept of *migasfree Golden Image* (MGI). We now have automated pipelines to build and deploy disk images optimized for hybrid BIOS/UEFI booting. Through attributes (such as the virtualization tag FLV-VIRTUAL), the system autonomously knows whether it should install a virtualized kernel and agents or support standard physical machines.
* **Project Templates**: It is now possible to export and import complete migasfree projects. In this way, you can define a reference configuration and use it as a base to deploy new implementations instantly.
* **migasfree Clone System**: System cloning tool. Thanks to migasfree Golden Images, this system allows you to clone machines quickly and easily.
* **High availability with pgpool**: Designed for environments with thousands of computers synchronizing simultaneously, v5 incorporates [pgpool-II](https://www.pgpool.net/). This component acts as a load balancer and connection pooler to the PostgreSQL database, guaranteeing fault tolerance, load balancing, and ultra-fast response times even for highly intensive queries.
* **File pool**: The classic static resources directory of v4 has transformed in v5 into a powerful file publication space managed through [Filebrowser](https://filebrowser.org/). This space allows you to upload and share in a centralized manner any type of resource or file that you need to make accessible to the clients in your park in a simple and secure way.
* **Security through mTLS**: Version 5 introduces native support for Mutual TLS (mTLS), establishing strict two-way authentication that validates both the server and clients to shield communications. This additional security layer is applied both to the workstations’ connections and to the access to administration web consoles, guaranteeing that only authorized machines and users can interact with the system.
* **Windows Integration**: Although migasfree has traditionally focused on GNU/Linux environment management, version 5 aims to break barriers and enter the Microsoft world. To achieve this elegantly and without compromising our philosophy of simplicity, [windows-package-tool](https://github.com/migasfree/windows-package-tool) (WPT) has been developed, a simplified package manager specifically designed for Windows. On the server side, the new `pms-wpt` service is responsible for building the Windows package repository.

  But integration does not stop at software deployment. To solve one of the biggest inventory headaches in hybrid fleets—uniform hardware reporting—[lshw-windows-emulator](https://github.com/migasfree/lshw-windows-emulator) has been developed. This emulator performs detailed queries to Windows Management Instrumentation (WMI) to identically simulate the XML/JSON output structure of the classic Linux `lshw` utility. In this way, the migasfree server processes the physical inventory of a Windows computer with the same naturalness and power that you have always enjoyed in Linux, achieving an insuperable technical cohesion.

I look back and surprise myself remembering that old white laptop where I developed the first prototype of migasfree. Seeing how the project has evolved, I cannot help but feel emotional about how far we have come. But beyond lines of code and new features, this journey has been a continuous learning process for me. And, as I realize it, I find myself smiling.

#### NOTE
If your organization is transitioning from a legacy migasfree v4 installation, on the [official migasfree website](https://migasfree.org) you will find the detailed procedure to convert your database and package repository to the new v5 service architecture.

\

## Capabilities

* We design for **simplicity**. Perhaps, seeing all the technology that supports version 5, this statement might sound contradictory. However, all that engineering has a single purpose: to absorb the internal complexity so you do not have to manage it.
* We advocate for **zero-touch management**. We ensure that everyday administration tasks are completely automated. A clear example of this is that client machines register automatically in the system; there is no need for you to register them manually on the server.
* It is based on the **client/server** architecture.
* It is **adaptable**. You can program your own `formulas` to obtain the `attributes` of computers and users according to your interests. This, combined with `Attribute Sets`, provides great versatility and power for any need.
* It is Free Software licensed under the **GNU General Public License**.
* It allows for creating both internal **package repositories** and caches of external repositories.
* It stores both the software and hardware **inventory** of the machines, allowing queries to be made on them. It also stores machine information such as their attributes, synchronizations, migrations performed, etc.
* **Error** management. Errors occurring on the machines are sent to the server and stored, allowing them to be tracked centrally.
* **Fault** management. You can program code that will run on clients to obtain machine information.
* **Alerts**. Provides real-time status of the system, facilitating the administrator’s work.
* **Statistics**. The administration web console displays various statistics of the data stored in the database.
* **Printers**. Provides efficient printer configuration deployment.
* **Applications**. Manages the applications that will appear in migasfree-play, allowing non-administrator users to install them easily.
* **Policies**. Establishes which packages are installed on computers based on their `attributes`.

\

## Software used

> > We are like dwarfs standing on the shoulders of giants, so that we can see more than they, and see further, not because our vision is sharper or our stature greater, but because we can raise ourselves higher thanks to their giant stature.

Listing all the software components used in migasfree would generate a list that is too extensive. Therefore, I will focus only on those I consider most relevant. However, it is crucial to highlight that each of them, even the library that might seem most modest, contributes to migasfree sitting on the shoulders of giants.

* Languages:
  * [Python](http://www.python.org/)
  * [Bash](https://tiswww.case.edu/php/chet/bash/bashtop.html)
  * [Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

* Web development frameworks.
  * [Django](https://www.djangoproject.com/)
  * [Vue](https://vuejs.org/)
  * [Quasar](https://quasar.dev/)

* ASGI (Asynchronous Server Gateway Interface) Server
  * [Uvicorn](https://uvicorn.dev/)

* Lightweight virtualization.
  * [Docker](https://www.docker.com/)
  * [Swarm](https://docs.docker.com/engine/swarm/)
  * [Portainer](https://www.portainer.io/)

* Reverse proxy
  * [HAProxy](https://www.haproxy.com/)

* Web file manager.
  * [Filebrowser](https://filebrowser.org/)

* Web server
  * [Nginx](https://nginx.org/)

* Distributed tasks and asynchronous processing.
  * [Celery](https://docs.celeryq.dev/en/stable/)
  * [Flower](https://flower.readthedocs.io/en/latest/)

* SQL Database
  * [PostgreSQL](http://www.postgresql.org/)
  * [pgAdmin](https://www.pgadmin.org/)

* NoSQL Database.
  * [Redis](https://redis.io/)
  * [RedisInsight](https://redis.io/insight/)

* GNU/Linux Distributions
  * [Debian](https://www.debian.org)
  * [Alpine Linux](https://alpinelinux.org/)

* Hardware Information:
  * [lshw](http://ezix.org/project/wiki/HardwareLiSter)

> #### NOTE
> One of the advantages of working with free software is the ease with which you can create projects, as you can mix different components without worrying too much about licensing issues. A wonderful example of this was the incorporation of hardware capturing functionality in the machines thanks to the [lshw](http://ezix.org/project/wiki/HardwareLiSter) command. With a few lines of code, I integrated it with the migasfree database from the very first versions.

With these foundations we conclude **Part I**. In **Part II (Getting Started)**, we make the leap to practice: you will set up your first migasfree laboratory, provision machines from scratch, and have a complete view of the software packaging and deployment cycle.

# II. Getting Started

Exploring the unknown challenges us, awakens emotions, and forces us to confront our insecurities, putting us to the test.

Change is never trivial. Whether on a personal, social, or scientific level, it always involves effort, uncertainty, and the challenge of dealing with internal and external barriers. It requires unlearning the old, adopting new perspectives, and often leaving the comfort of the familiar. This process, far from being simple, demands time, energy, and courage. It is natural for it to generate resistance, whether out of fear, insecurity, or the inherent difficulty of breaking established patterns. Therefore, every small step that brings us closer to change is an achievement that deserves to be recognized and celebrated.

Although challenging, change provides us with valuable opportunities to grow, learn, and adopt new ways of working. In this same spirit of transformation, I invite you to explore migasfree, a tool created to drive efficient and positive change in operating system management.

In this second part of Fun with migasfree, I will explain how to install a migasfree server and client in a **test laboratory**. My intention is for you to start experimenting with the tool as soon as possible.

Please note that the configurations and simplifications we make in this section are designed exclusively for this testing and learning environment. In a real environment, infrastructure deployment requires the use of valid DNS domain names (FQDN) and corporate certificates (which we will cover in Part III), as well as rigorous planning for high availability, sizing, and business continuity (which we will see in Part IV).

If in the first part of this book we saw the theory, now it is time to put it into practice and explore the comprehensive process of Software Configuration Management (SCM).

You will learn how to:

* Create configuration changes the migasfree way.
* Automatically install software along with its configurations through centralized deployments.
* Track, control, and audit these changes, following SCM best practices.

Let’s get to it!

# Laboratories

> In theory there is no difference between theory and practice. In practice there is.

This chapter guides you through creating a virtualized lab on your own computer, allowing you to perform all the practical exercises in the book without requiring dedicated physical infrastructure.

Architecture of the Laboratory

## *Laboratory architecture*

This lab consists of two virtual machines running on [VirtualBox](https://www.virtualbox.org/):

**manager** (192.168.1.5): Server hosting the full migasfree stack in Docker Swarm.

**VM-001** (192.168.1.101): Client workstation managed by migasfree.

Both machines communicate over a local network using **bridged adapter** mode, allowing direct access from your host machine.

```bash
sudo usermod -aG vboxusers,disk $USER
```

#### NOTE
Laboratory Requirements

\

### A host computer with a 64-bit architecture (x86_64).

At least **8 GB of RAM** (16 GB recommended to smoothly run both VMs alongside your operating system).

At least **40 GB of free disk space**.

> * VirtualBox 7.x or higher installed on your host machine.

An ISO image of Debian 13 (Trixie) or Debian 12 (Bookworm) minimal/netinst.

> * Hardware-assisted virtualization enabled in the host BIOS/UEFI (VT-x / AMD-V).
> * Creating the Base Virtual Machine
> * To optimize time and disk space, we will first create a base virtual machine that we will later clone to obtain both nodes (`manager` and `VM-001`).
> * In VirtualBox, create a new virtual machine with the following parameters:
> * **Name**: `base-debian`

#### NOTE
**RAM Memory**: 2048 MB (2 GB)

\

### **Hard Disk**: 20 GB (dynamic allocation)

We will install the migasfree server on [Debian Trixie](https://www.debian.org/), although it can also be deployed on [Ubuntu](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/) or any other modern GNU/Linux distribution that supports Docker.

Attach the Debian ISO and perform a minimal installation (without a desktop environment). During installation:

> * Configure user: `vbox` with password `vbox` (or your preferred user).
> * Do not install an SSH server or graphical environment at this stage (we will install them later as needed).
> * Once the installation finishes, shut down the virtual machine.
> * Cloning the Virtual Machines
> * We will now generate the two lab nodes from `base-debian`:
> * Manager Node
> * In VirtualBox, right-click on `base-debian` and select **Clone**:

Clone type: **Linked clone** (to save disk space) or **Full clone**.

MAC Address Policy: **Generate new MAC addresses for all network adapters**.

Adjust resources for the `manager` machine: assign **4096 MB of RAM** (4 GB) and **2 vCPUs** in the virtual machine settings.

Client Node (VM-001)

Right-click on `base-debian` and select **Clone**.

* Clone type: **Linked clone**.

MAC Address Policy: **Generate new MAC addresses for all network adapters**.

Click **Next**.

> * Name: **VM-001**

Click **Finish**.

\

#### Configuring the Manager Virtual Machine

In the settings of the manager virtual machine, change the network adapter to **Bridged Adapter** and select your active network interface (Ethernet or Wi-Fi).

Start the `manager` virtual machine.

Once the virtual machine has booted and you have logged in with the `vbox` user, switch to the `root` superuser to perform administrative tasks.

Open a terminal and log in as the privileged user (*root*):

> ```bash
> sudo su
> ```

To prevent `NetworkManager` from interfering with static network management, disable it if present:

> ```bash
> systemctl stop NetworkManager
> systemctl disable NetworkManager
> ```

Edit the `/etc/network/interfaces` file:

> ```bash
> nano /etc/network/interfaces
> ```

Add the static configuration to the end of the file, replacing values according to your local subnet:

> ```text
> auto enp0s3
> iface enp0s3 inet static
>     address 192.168.1.220
>     netmask 255.255.255.0
>     gateway 192.168.1.1
> ```

In our lab, the static IP address we will use is `192.168.1.5` on interface `enp0s3` (or the corresponding interface name on your machine):

Configure the DNS server in `/etc/resolv.conf`:

> ```bash
> echo "nameserver 8.8.8.8" > /etc/resolv.conf
> ```

Next, add the migasfree server resolution lines to the `/etc/hosts` file:

> ```bash
> cat <<EOF >> /etc/hosts
> 192.168.1.220 migasfree.acme.com
> 192.168.1.220 portainer-migasfree.acme.com
> 192.168.1.220 datastore-migasfree.acme.com
> 192.168.1.220 database-migasfree.acme.com
> 192.168.1.220 datashare-migasfree.acme.com
> 192.168.1.220 worker-migasfree.acme.com
> EOF
> ```

Flush the IP address previously assigned via DHCP and restart the networking service:

> ```bash
> ip addr flush dev enp0s3
> systemctl restart networking
> ```

Verify that the FQDN resolves correctly by testing network connectivity:

> ```bash
> ping migasfree.acme.com
> ```

> ```text
> PING migasfree.acme.com (192.168.1.220) 56(84) bytes of data.
> 64 bytes from migasfree.acme.com (192.168.1.220): icmp_seq=1 ttl=64 time=0.611 ms
> ```
\

#### Docker Installation

To install Docker, run the following commands adapted from the [official Docker documentation](https://docs.docker.com/engine/install/debian/#install-using-the-repository):

> ```bash
> apt-get update
> apt-get install -y ca-certificates curl
> install -m 0755 -d /etc/apt/keyrings
> curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
> chmod a+r /etc/apt/keyrings/docker.asc
> echo \
>   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
>   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
>   tee /etc/apt/sources.list.d/docker.list > /dev/null
> apt-get update
> apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
> ```

Verify that Docker is installed:

> ```bash
> docker version
> ```

#### migasfree-swarm

Now we will install the migasfree cluster. To do this, we will retrieve the latest version of migasfree-swarm:

> ```bash
> wget -O - http://migasfree.org/pub/install-swarm | bash
> ```

#### NOTE
This script automatically downloads the latest released version of the deployment tool and configures it in your environment.

Initialize the configuration:

> ```bash
> migasfree-swarm config
> ```

Set DATASHARE_FS to: **local**

> ```text
> DATASHARE_FS (local | nfs): local
> ```

Download the Docker images.

> ```bash
> migasfree-swarm pull
> ```

Deploy the server:

> ```bash
> migasfree-swarm deploy
> ```

Now enter a name for the STACK and the FQDN:

> ```text
> STACK(): test
> FQDN: migasfree.acme.com

> Warning! This system is not a Swarm node.
> Do you want to create a manager node? (Y/n): Y
> ```

#### NOTE
The **STACK** is the service stack identifier in Docker Swarm. If you run a single instance, you can use `migasfree` as the default name.

Wait for the base services to initialize. When “migasfree we are ready” appears, you can access the web console:

#### NOTE
Because a self-signed certificate was generated, a security warning will appear in your browser. Accept the certificate to proceed.

Wait for the remaining services to start (everything should show up in green):

### A First Look at the Server

To log in to the web console, first retrieve the administrative credentials:

> ```bash
> migasfree-swarm secret
> ```

You will get output similar to the following:

> ```text
> root@migasfree-server:/home/vboxuser# migasfree-swarm secret

> ● portainer:

>     LxtaOymswAqu GcdryHnjrCitEUZgMgpDd0S3yVY1FU

> ● Stack test:

>     ● database_console:

>         HMnjPZIBUA9p@migasfree.acme.com X2RO7fA6qumPJCSyLfeSKgBjwlmKRroL

>     ● Others:

>         HMnjPZIBUA9p X2RO7fA6qumPJCSyLfeSKgBjwlmKRroL
> ```

Notice that three pairs of credentials (username and password) are displayed:

* **portainer**: for Docker container management access.
* **database_console**: for connecting to the database console.
* **Others**: for authenticating to the migasfree web console and all remaining services.

#### NOTE
These credentials constitute the root or *bootstrap* account generated during initial cluster deployment. Store them securely.

Click on the migasfree console icon.

Log in by entering the credentials from the **Others** section.

As expected, there are no registered computers yet.

At this point, we will shut down the `manager` virtual machine to take a snapshot in VirtualBox, allowing us to restore this clean initial state at any time.

> ```bash
> systemctl poweroff
> ```

#### NOTE
Always perform a clean shutdown of the virtual machine (by running `systemctl poweroff` as root or using VirtualBox’s ACPI shutdown option) before taking a snapshot.

Finally, boot the `manager` virtual machine and verify that the services are active:

Congratulations! Your migasfree server is now fully operational. We made it quick and easy, didn’t we?

### Configuring the VM-001 Virtual Machine

Now start the `VM-001` machine and access its terminal.

#### Network and Identity Configuration

Access the terminal as user `root`:

> ```bash
> sudo su
> ```

Set the hostname and update `/etc/hosts`:

> ```bash
> hostnamectl set-hostname VM-001.acme.com
> sed -i 's/127.0.1.1.*/127.0.1.1       VM-001.acme.com VM-001/' /etc/hosts
> ```

Next, add the migasfree server resolution lines to the `/etc/hosts` file:

> ```bash
> cat <<EOF >> /etc/hosts
> 192.168.1.220 migasfree.acme.com
> 192.168.1.220 portainer-migasfree.acme.com
> 192.168.1.220 datastore-migasfree.acme.com
> 192.168.1.220 database-migasfree.acme.com
> 192.168.1.220 datashare-migasfree.acme.com
> 192.168.1.220 worker-migasfree.acme.com
> EOF
> ```

Verify that domain names (FQDN) resolve correctly:

> ```bash
> ping migasfree.acme.com
> ```

> ```text
> PING migasfree.acme.com (192.168.1.220) 56(84) bytes of data.
> 64 bytes from migasfree.acme.com (192.168.1.220): icmp_seq=1 ttl=64 time=0.611 ms
> ```

#### Installing the Self-Signed CA Certificate

Add the CA certificate used to self-sign the migasfree server’s SSL certificate to the operating system’s trust store:

> ```bash
> wget --no-check-certificate \
>   -O /usr/local/share/ca-certificates/ca-migasfree.acme.com.crt \
>   https://migasfree.acme.com/pool/install/ca-migasfree.acme.com.crt

> /usr/sbin/update-ca-certificates --fresh --verbose
> ```

#### Installing migasfree-play, migasfree-client, and migasfree-agent

In the same terminal, as user `root`:

> ```bash
> wget -O - http://migasfree.org/pub/install-client-v5-fwm | bash
> ```

This will install the packages `migasfree-play`, `migasfree-client`, and `migasfree-agent` on the client system.

Next, configure the migasfree client to indicate which server it should connect to:

> ```bash
> migasfree conf --server migasfree.acme.com
> ```

This command updates `/etc/migasfree.conf`, setting the server URL to `https://migasfree.local`.

> ```ini
> [client]
> Server = migasfree.acme.com
> ```

Although we just modified the client configuration with this command, remember the Golden Rule of systems management:

> #### NOTE
> All application and operating system configuration changes must be packaged and managed centrally through migasfree, avoiding manual changes to client files.

## Synchronization

Synchronization is the process by which the client contacts the server, sends its hardware and software inventory (attributes), and applies the assigned deployments.

Run the synchronization command as user `root`:

> ```bash
> migasfree sync
> ```

You will see output similar to this (observe all the steps performed during synchronization):

> ```text
> root@VM-001:/home/vboxuser# migasfree sync
> migasfree version: 5.0

> Config options: /etc/migasfree.conf
>         Project: debian-gnu-linux-13 (DEFAULT)
>         Server: https://migasfree.acme.com (FILE)
>         Auto update packages: True (DEFAULT)
>         Manage devices: True (DEFAULT)
>         Upload hardware: True (DEFAULT)
>         Proxy: None (DEFAULT)
>         Package Proxy Cache: None (DEFAULT)
>         Debug: False (DEFAULT)
>         Computer name: VM-001 (DEFAULT)

> Running options:
>         migasfree server version: 5.0
>         SSL certificate: /tmp/migasfree-client/cert.pem
>         PMS: apt
>         Architecture: amd64
>         Graphic user: vboxuser

> -> Connecting to migasfree server...
> -> Getting properties...
> -> Evaluating attributes...
> -> Uploading attributes...
> -> Getting fault definitions...
> -> Executing faults...
> -> Uploading faults...
> -> Getting repositories key...
> -> Getting repositories...
> -> Creating repositories...
> -> Getting repositories metadata...
> -> Getting mandatory packages...
> -> Uninstalling packages...
> -> Installing mandatory packages...
> -> Updating packages...
> -> Uploading software...
> -> Getting devices...
> -> Getting traits...
> -> Ending synchronization...
> -> Completed operations
> ```

## Verification

Verify the data gathered by the server by accessing the migasfree web console at `https://migasfree.local`.

* Look at the alerts section (you can see 3 initial alerts as shown in the image):
  > 
* Navigate to the computers section by clicking the `Computer` icon and then `Computers`:
  > * Click on `CID-1` to inspect the full details of the registered computer.
  > * Check the date and time of the last synchronization.
  > * Review the *hardware* inventory by clicking on the `product` field.

  > 

  #### NOTE
  The **CID** identifier stands for *Computer IDentificator*, a unique numeric identifier assigned sequentially to each computer upon its first registration with the server.

Congratulations again! You have registered your first computer in migasfree.

## migasfree Agent

Earlier we installed the `migasfree-agent` package on VM-001. This background service maintains a persistent connection with the server via WebSocket, enabling real-time actions without waiting for scheduled periodic synchronization.

However, it is necessary to restart this service because it was started before configuring the server address in `/etc/migasfree.conf`:

```bash
systemctl restart migasfree-agent
```

From the computer’s detail page in the migasfree web console, you can perform immediate actions:

* **Immediate synchronization**: Force the computer to execute `migasfree-client` on demand.
* **Remote control**: Launch **SSH** (command-line console), **VNC** (graphical desktop sharing), or terminal sessions directly from your browser.

## migasfree Play

We also installed the `migasfree-play` package on the `VM-001` virtual machine.

This is a graphical software center designed for end users, allowing them to install, update, and remove organizational software with a single click, without requiring administrative privileges (*root*).

We can launch `migasfree-play` from the VM-001 applications menu or by executing `migasfree-play` in a terminal.

#### NOTE
Do not worry if we have only touched upon these tools briefly. In upcoming chapters, we will explore each of them in depth.

## Deployment

To conclude this hands-on lab introduction, we will perform a first practical deployment exercise.

Imagine a common administrative scenario: you want to replace the nano editor with vim across all client computers in your organization.

Navigate to the **Deployments** section in the migasfree web console, click **New**, and fill in the fields:

* **Name**: replace nano with vim
* **Project**:  *(select the project corresponding to your client)*
* **Origin**: Internal
* **Packages to install**: vim
* **Packages to uninstall**: nano
* **Included attributes**: SET-ALL SYSTEMS

Save the deployment. Next, in the client machine’s terminal, force a synchronization:

> ```bash
> migasfree sync
> ```

In the terminal output, you will observe the client downloading metadata from the new deployment, uninstalling nano, and installing vim automatically.

> ```text
> -> Obteniendo los metadatos de los repositorios...

> ...

> Des:8 https://migasfree.acme.com/public/debian-gnu-linux-13/repos sustituir-nano-por-vim
> InRelease [2.059 B]

> ...

> -> Diferencia en el software

> {'installed': ['+vim-runtime_2:9.1.1230-2_all.deb', '+vim_2:9.1.1230-2_amd64.deb'],
> 'uninstalled': ['-nano_8.4-1+deb13u1_amd64.deb']}
> ```

By assigning the `SET-ALL SYSTEMS` attribute, this policy applies universally to all computers registered in the project.

In this first exercise, we limited ourselves to managing packages already available in Debian’s official repositories (which migasfree orchestrates). In subsequent chapters, you will learn how to package and deploy your own custom software and configurations.

If you wanted to modify this policy in the future (for instance, to add emacs as well), you would simply edit the deployment in the console:

* **Packages to install**: vim emacs
* **Packages to uninstall**:  *(blank)*

As machines across your network run their periodic synchronizations, they will converge automatically to the newly defined Desired State.

## Mission Accomplished

Congratulations! In this first practical session, you have deployed a full migasfree server in Docker Swarm, configured a client workstation, synchronized inventories, and executed your first software deployment policy.

In the next chapter, you will learn how to provision computers from bare metal using MCS (Migasfree Cloning System), the automated network deployment and cloning system.

# Mass Provisioning

> Speed is useful only if you are running in the right direction.

In large organizations, installing and configuring workstations one by one is an unfeasible task. While the package management system solves software maintenance throughout the machine’s lifecycle, the initial deployment requires an agile, unattended, and reproducible method to install the operating system across hundreds or thousands of computers.

Historically, system administrators have resorted to disk cloning techniques using tools like Clonezilla, Ghost, or Fog. However, traditional cloning has significant limitations: images are monolithic, easily become outdated, and require regenerating huge files every time software changes.

* migasfree solves this problem through an integrated approach that combines automated Master Image generation from the web console with an agile, modular deployment system called **MCS** (*Migasfree Cloning System*).
* A Master Image is a base operating system template configured with specific parameters, used as a model to deploy multiple identical systems across an organization.

In traditional environments, creating a master image requires installing a machine, manually customizing it, shutting it down, and capturing its disk state. In migasfree, this process is completely inverted and automated: **you do not capture an image, you declare and build it**.

Mass provisioning in migasfree revolves around two complementary components:

**MGI (Migasfree Golden Image)**: The build engine that creates customized Master Images from recipes and definitions in the web console.

**MCS (Migasfree Cloning System)**: The client deployment tool running on a lightweight Alpine Linux environment, capable of cloning images over the network (HTTP/NFS) or from local media.

* *Architecture of the MGI and MCS ecosystem*
* Master Image Generation (MGI)

#### NOTE
The creation of Master Images in migasfree is managed from the **Master Images** menu in the web console. This engine automates the entire process of downloading packages, building filesystems, and generating compressed deployment images.

Unlike traditional monolithic images, MGI builds images in a modular way:

## **Base filesystem**: Minimal operating system installation generated with native tools (such as `debootstrap` for Debian/Ubuntu or `dnf/yum` for RPM distributions).

**Flavours**: Modular software layers that are added on top of the base image to specialize the system (e.g., a minimal server, an administrative desktop, or a lab workstation).

The MGI architecture in the web console is structured across four levels:

1. **Configurations**: Define the technical baseline of the operating system (distribution, architecture, partitions, and base scripts).
2. **Flavours**: Allow creating variants on top of the same configuration without having to duplicate base definitions.
3. **Releases**: Represent stable tagging and versioning of the image set.
4. **Builds**: The automated compilation and generation process that produces deployable .mgi files.

#### NOTE
Image availability for deployment is controlled via the **promoted** property. An image will not appear in the MCS deployment menu until it is marked as promoted, preventing the inadvertent deployment of versions still undergoing testing.

## MCS Deployment

Once the MGI image is published in the server catalog, **MCS** comes into play. It is a live environment distributed as a bootable ISO image that transforms any USB flash drive or network PXE boot into an unattended mass installation station.

### Obtaining the Boot Media

The MCS ISO image file (mcs-<version>.iso) is preconfigured and available directly from the migasfree server or from the official project repository.

To write the ISO to a USB drive of at least 4 GB (32 GB or more is recommended if you wish to store images locally), you can use graphical tools such as [balenaEtcher](https://etcher.balena.io/) or [Rufus](https://rufus.ie/), or the GNU/Linux command-line utility:

> ```bash
> sudo dd if=mcs-version.iso of=/dev/sdX status=progress
> ```

#### NOTE
On the first boot from the USB drive, MCS will automatically expand its storage partition to use the entire remaining capacity of the drive, creating space to store local MGI images and logs.

### User Interface Operations (TUI)

When booting the target machine from the boot media (selecting UEFI or Legacy boot according to the system), MCS presents a text-based interface (TUI) with the following main operations:

* **Network Clone**: Streams the MGI image directly from the migasfree server over HTTP or NFS, without saving the image locally. Ideal for environments with gigabit networks.
* **Local Clone**: Clones an MGI image previously stored on the USB drive itself, allowing installations in places without network connectivity or with limited bandwidth.
* **User Data Preservation (Preserve HOME)**: When selecting a deployment project, MCS detects whether the disk already contains a /home partition from an earlier installation. If requested, it preserves user documents and configurations while reinstalling the root operating system partition.

  #### NOTE
  For security reasons, MCS verifies that the user with UID `1000` corresponds to the same username on both the old and new installations before preserving /home.
* **Local Images**: Allows listing, downloading, updating, or deleting MGI images stored on the USB drive.
* **Settings**: Allows customizing the URL or IP address of the migasfree server, the active project, and proxy parameters if necessary.

## The Complete Lifecycle

The integrated mass provisioning workflow is summarized in three synchronized phases:

1. **CI Phase (Web Console Build)**: The MGI is defined and built from the web console. Packages are downloaded, partitions are configured, and the .mgi image is compiled.
2. **CD Phase (Technician Operation with MCS)**: The technician boots the target computer from the USB drive, selects the image, and deploys it in minutes.
3. **Handover to migasfree**: Upon finishing image deployment, the computer boots into the new operating system, automatically runs `migasfree-client`, self-registers with the server, sends its hardware inventory, and applies assigned post-deployment policies.

## Hands-on Practice

To consolidate the concepts covered in this chapter, we will perform a complete hands-on exercise: from importing a preconfigured template to cloning a virtual machine using MCS.

The fwm template provides a base definition on Debian 13, designed specifically for the book’s exercises. It includes:

* **Partition layout** (`partition.yml`) optimized for desktop workstations.
* **Default flavour** (`workstation` in `flavours.yml`), configured with a lightweight graphical environment (LXDE).
* **Deployments and applications** (`deployments.yml` and `applications.yml`) ready to be tested.

Official migasfree templates are hosted in the public [project-templates](https://github.com/migasfree/project-templates) repository on GitHub. This repository gathers packaged and preconfigured projects for various distributions, allowing full projects to be easily imported directly from the web console.

### Step 1: Import the fwm Template and Build the MGI

1. Import the fwm template into the migasfree console.

   Navigate to the **Settings > Projects** menu in the migasfree web console and click **Import**:
   * **Catalog Origin**: Remote
   * **Template**: fwm
   * **Project Name**: FWM

   

   Upon saving, the `FWM` project will be created automatically, along with its configuration records, flavours, deployments, and predefined applications.

   Navigate to the **Release > Deployments** menu and observe that the deployments defined in the template have been imported.
   

   Click on the `FWM` line to access details. Take a moment to explore how each deployment is structured.
   
2. Build the Master Image

   Navigate to the **Master Images > Releases** menu and add a new release for the `FWM` configuration:
   * **Configuration**: FWM
   * **Version**: 1.0
   * **Release Notes**: Testing initial release.

   Click the `Save and continue editing` button.
3. Launch the Build

   Click on the `Launch build` button:
   

\

The server will begin building the Master Images (MGI). This process may take a few minutes as it downloads base packages and generates the filesystems.

Navigate to the **Master Images > Releases > FWM 1.0** menu to observe the build status.

Once builds complete successfully, you will observe that the MGI images have been generated for each defined flavour (e.g., `fwm-1.0-workstation.mgi`).

Images are published at the URL path `https://migasfree.local/pool/mgi/` (or the corresponding FQDN in your environment).

You might wonder at this point: how were these two flavours defined? If you navigate to **Master Images > Configurations > FWM > Flavours**, you will see the definition of `server` and `workstation`.

You will now see the `LXDE` deployment filtered. If you edit it to see how it is defined, you will notice that anyone assigned the `FLV-LXDE` attribute must have `firefox-esr`, `fonts-dejavu-core`, `fonts-freefont-ttf`, `lightdm`, `lxde-core`, and `migasfree-play` installed. This installs the desktop environment on top of the minimal base image defined in the [template](https://github.com/migasfree/project-templates/blob/main/fwm/dockerfile.j2) (which corresponds to the default flavour, `server`).

### Step 2: Creating the Bootable USB with MCS

1. Download the MCS ISO image (`mcs-x.x.iso`) published in the server directory or from the official releases repository.
2. Plug a USB drive of at least 4 GB into your administration machine. To write the ISO image to the device, you can use graphical utilities such as [balenaEtcher](https://etcher.balena.io/) or [Rufus](https://rufus.ie/), or the `dd` command-line tool on GNU/Linux:
   ```bash
   sudo dd if=mcs-1.2.iso of=/dev/sdX status=progress
   ```

    *(Make sure to replace \`\`/dev/sdX\`\` with the correct identifier of your USB drive)*.

> With this step completed, you now have a bootable USB drive with MCS, ready to deploy master images on any computer on the network.

### Step 3: Cloning FWM workstation onto the `VM-001` Virtual Machine

Now we will use the USB flash drive with MCS to boot and clone `FWM workstation` onto our client virtual machine `VM-001`.

1. Plug the bootable **MCS** USB drive into the lab host PC.
2. Run the following commands to create a raw VMDK virtual disk mapping directly to your physical USB drive:
   ```bash
   sudo VBoxManage createmedium disk   --filename ~/mcs-1.2.vmdk   --format VMDK   --variant RawDisk   --property RawDrive=/dev/sdX
   sudo chown $USER:$USER ~/mcs-1.2.vmdk
   ```
3. Attach the VMDK virtual disk to the `VM-001` virtual machine:

   Navigate to **Settings > Storage** and add the `mcs-1.2.vmdk` file as a hard disk on the SATA controller.

1. Start the `VM-001` virtual machine, press F12 during boot to access the boot menu, and select the USB drive.

1. Select the **Network Clone** option. You will see a message indicating that no promoted images were found.

1. Now, select the **Network Clone** option again and the available images list will be displayed.

   Select the remote image **fwm 1.0-workstation**.

   The target disk sda (60 GB) appears, which is disk 1 where the previous system is currently installed.

   Set hostname to: **VM-001**
2. Finally, confirm the start of the cloning process. MCS will partition the disk, format filesystems, and download and extract the MGI image.

   Press `Yes` and do not leave—this takes less than a minute! Watch how MCS unpacks the system at high speed.

1. From the MCS menu, select **Poweroff** to shut down the virtual machine.

### Step 4: Verification and First Boot

Once cloning is complete, remove the USB drive from **Settings > Storage** in VirtualBox, and start `VM-001` normally.

1. The system will boot directly into the fresh installation of the `FWM` project with the LXDE graphical environment.
2. Log in with username migasfree and password migasfree. These credentials were configured in the project template.
3. Let migasfree-play synchronize the virtual machine.
4. In the LXDE menu, open **System > migasfree-play**. Notice that you now have the software catalog available.

   Notice that you can install `gimp` without being root—try it!

   Do you know where applications are published? Very simple: in the migasfree web console under **Configuration > Applications**.

1. Now check the computer `CID-1` in the migasfree web console by navigating to **Computers > Computers > CID-1 > Migrations**:

## Another success!

Congratulations! You have successfully completed the entire mass provisioning lifecycle: from declaring and building a Golden Image in the cloud/server, to flashing it onto a machine in seconds with MCS and watching it self-configure on first boot.

In this chapter, you have learned to:

* **Build Master Images (MGI)**: Import a project template and compile modular operating system images from the web console.
* **Manage MGI visibility**: Use the *promoted* property to safely control which images are ready for production deployment.
* **Prepare boot media**: Create a bootable USB drive with **MCS** and configure it to deploy systems over the network or locally.
* **Execute unattended cloning**: Automate disk partitioning and image extraction in under two minutes per workstation.
* **Verify software self-service**: Confirm client self-registration and explore end-user application installation via `migasfree-play`.
* **Track migration history**: Review how migasfree logs every reinstallation in the computer’s central lifecycle history.

It has been an intense journey, but you made it! It is completely normal if many concepts feel new right now. In Part III of the book, we will break down each of these components in depth.

For now, in **Chapter 7** we will take the next logical step and address: how do we manage physical servers with migasfree?

# Packaging

> > Do not wait until the conditions are perfect to begin. Beginning makes the conditions perfect.

Having covered the **initial provisioning** phase in the previous chapter, we now face the ongoing challenge of systems administration: managing change throughout the lifecycle of workstations.

The goal of this chapter is to learn how to manage system and application configuration through **custom software packaging**, following a structured methodology that ensures traceability, reproducibility, and total control over changes.

We enter fully into **Software Configuration Management as a whole**. To see this entire process in practice, we will deploy a package that will install sample files (PNG, GIF, MP4, etc.) to help User Support Center ([CAU](https://en.wikipedia.org/wiki/help_desk)) staff verify file and application associations.

## The Traditional Way

Imagine receiving a change request to add sample files for multimedia extensions across all GNU/Linux desktops in your organization, so that support staff can test file associations.

Since you have not yet established how to deploy software to GNU/Linux desktops, you decide to copy the files manually to a few machines or distribute them via an ad-hoc script.

Now then, while you are on vacation, could a colleague easily answer the following questions?

* What changes have been made to a specific machine since May 1st?
* Who made the change?
* When were all those changes deployed to the machines?
* Which computers currently have a specific change applied?

Your colleague will hardly be able to answer these questions quickly and reliably.

And worse yet: what happens to computers that were turned off? They simply missed the script execution and remain in an inconsistent state.

You could have saved yourself a lot of effort by using configuration management tools. But let us see how we do it properly.

Integrity against change is not guaranteed with this method.

## The migasfree Way

Below, I propose the method for implementing configuration changes using migasfree:

> #### NOTE
> Use the wheel; do not reinvent it. By using the packaging system to deploy our configuration, we leverage the integrity that the package manager already provides.

I assume you have a **project manager** like [Redmine](https://www.redmine.org/) where you register change requests (or at least pretend you do) and that you have successfully completed the previous chapter.

> #### IMPORTANT
> Before continuing, verify that the `manager` virtual machine is running and accessible.

> All commands in this chapter will be executed in the `VM-001` virtual machine as the `root` user.

### Your First Configuration Change

The first change to a **Software Configuration Item** (SCI) will consist of creating and deploying a Debian package called `acme-test-files`.

#### Request

Imagine receiving the following change request, which you log in your project manager:

The first thing you do is identify the affected SCI—that is, which package needs to be created or modified:

#### Change

##### Packaging

As a developer, you need to create the configuration package `acme-test-files`.

> ```bash
> sudo apt-get install unzip wget
> wget https://github.com/migasfree/fun-with-migasfree-examples/archive/master.zip
> unzip master.zip
> cd fun-with-migasfree-examples-master
> ```

Observe the files we will include in the `acme-test-files` package:

> ```bash
> ls -la acme-test-files/usr/share/acme-test-files/
> ```

You now have the package source. Next, build the package. First, install the development tools:

> ```bash
> sudo apt-get install devscripts gcc build-essential:native
> ```

And now, build the package:

> ```bash
> cd acme-test-files
> /usr/bin/debuild --no-tgz-check -us -uc
> cd ..
> ```

Congratulations, the change is packaged in `acme-test-files_1.0_all.deb`!

##### Uploading the Change to the Server

Next, upload the newly built package to the migasfree server:

> ```bash
> sudo migasfree upload -f acme-test-files_1.0_all.deb
> ```
* Enter username and password (packager credentials).
* Project: FWM
* Destination store: (leave blank to upload to the default store)
  ```text
  migasfree@VM-001:~/fun-with-migasfree-examples-master$ sudo migasfree upload -f acme-test-files_1.0_all.deb
  migasfree version: 5.0

  Config options: /etc/migasfree.conf
          Project: FWM (DEFAULT)
          Server: https://migasfree.acme.com (FILE)
          Auto update packages: True (DEFAULT)
          Manage devices: True (DEFAULT)
          Upload hardware: True (DEFAULT)
          Proxy: None (DEFAULT)
          Package Proxy Cache: None (DEFAULT)
          Debug: False (DEFAULT)
          Computer name: VM-001 (DEFAULT)
  User to upload at server: YD67skgwb1VM
  User password:
  Project to upload at server: FWM
  Store to upload at server: acme
  ```

Log the change in your project manager:

Congratulations! You made a configuration change and stored it safely on the server.

#### Release

Now you will see the perspective of the release manager responsible for deploying changes:

Access your server via a web browser. Notice that in `Alerts` you have an alert showing: `orphan packages`.

##### Releasing the Configuration Change

Now, you will release the change by creating a new *deployment*.

To do this, navigate to the **Release > Deployments** menu.

Click on the `+` button to `add a new internal deployment`:

* Name = `CAU test-files`
* Project = `FWM`
* Origin = `Internal`
* Available packages = `acme-test-files_1.0_all.deb`

  This field assigns the packages that the physical repository on the server will contain.
* Packages to install = `acme-test-files`

  This field lists the **names** of the packages that will be installed on client computers.
* Included attributes = `SET-ALL SYSTEMS`

  This indicates that all clients in the project will have access to this deployment.

Save the deployment.

Notice that in `Alerts`, you no longer have any orphan packages.

Log and close the change request:

##### Applying the Change

Apply the change to `VM-001`:

> ```bash
> sudo migasfree sync
> ```

Notice that the command output displays `acme-test-files` in the list of installed packages.

You can verify that your sample files now reside in /usr/share/acme-test-files.

> ```bash
> ls -la /usr/share/acme-test-files
> ```

### Your Second Configuration Change

#### Request

A second change request arrives: your colleagues at the CAU liked the sample files and now request an SVG vector file.

As always, you first identify the affected SCI: in this case, the existing `acme-test-files` package.

#### Change

Changes made to an already existing package are usually simpler:

##### Packaging

Download the SVG file from [https://commons.wikimedia.org/wiki/File:Tux.svg](https://commons.wikimedia.org/wiki/File:Tux.svg) to the `acme-test-files/data/usr/share/acme-test-files/` directory.

> ```bash
> wget https://commons.wikimedia.org/wiki/File:Tux.svg \
>   -O acme-test-files/usr/share/acme-test-files/tux.svg
> ```

Edit the package file `acme-test-files/debian/changelog` to log the new version:

> ```bash
> nano acme-test-files/debian/changelog
> ```

You will need to **add** these lines **to the top of the file**:

> ```text
> acme-test-files (1.1) unstable; urgency=low

>   * Added file tux.svg

>  -- Alberto Gacías <alberto@migasfree.org>  Fri, 3 Feb 2018 18:25:00 +0100
> ```

Pay attention to:

* The package version **(1.1)**.
* Replacing **your name and email address**.
* Updating the **date and timestamp**.
  > #### NOTE
  > The format used in Debian package **changelogs** is **very strict**.

One aspect not to overlook is *copyright* and licensing:

> ```bash
> nano acme-test-files/debian/copyright
> ```

and add the copyright and license information for the tux.svg file.

> ```text
> Files: tux.svg
> Copyright: lewing@isc.tamu.edu Larry Ewing and The GIMP
> License: https://creativecommons.org/publicdomain/zero/1.0/legalcode
> ```

Now, build the package:

> ```bash
> cd acme-test-files
> /usr/bin/debuild --no-tgz-check -us -uc
> cd ..
> ```

Notice that the same package has been generated, but with version `1.1`:

> ```bash
> ls -la *.deb
> ```

> ```text
> -rw-r--r-- 1 root root 2338 feb  3 17:49 acme-test-files_1.0_all.deb
> -rw-r--r-- 1 root root 2398 feb  3 18:27 acme-test-files_1.1_all.deb
> ```

##### Uploading the Change to the Server

> ```bash
> sudo migasfree upload -f acme-test-files_1.1_all.deb
> ```
* Enter username and password.
* Project: FWM
* Destination store: (leave blank to upload to the default store)

#### Release

##### Releasing the Configuration Change

Notice how an `orphan package` appears in `alerts` again, because version 1.1 is not yet assigned to any deployment.

Navigate to **Release > Deployments** in the migasfree web console and edit the `CAU test-files` deployment:

Add package `acme-test-files_1.1_all.deb` to `Available packages`.

Save the deployment.

Log and close the change request:

##### Applying the Change

Run synchronization again:

> ```bash
> sudo migasfree sync
> ```

Observe the software update in the command output:

> ```text
> -> Software diff

> {
>     'installed': ['+acme-test-files_1.1_all.deb'],
>     'uninstalled': ['-acme-test-files_1.0_all.deb']
> }
> ```

Verify that the change has been applied:
: ```bash
  ls -la /usr/share/acme-test-files
  ```

The `tux.svg` file we added in package version 1.1 should now be present.

## Auditing

Now your colleague would indeed be able to answer the following questions easily:

### What changes occurred on computer `CID-001` and when?

In the migasfree web console, go to **Data > Computers**. Edit computer `CID-1` and check the `Software Changes` tab.

The minus sign (-) indicates uninstalled packages and the plus sign (+) indicates installed packages.

### What was changed, who made the change, and when?

This information is embedded in the package metadata. To access it, query the package changelog:

Here you can see the history of changes (among other metadata):

### Which machines have the `acme-test-files-1.1` change installed?

Go to the **Release > Packages** menu, filter by package `acme-test-files`, and click on the installed computers count.

\

## Automation

In professional environments with dozens of configuration packages and multiple target distributions, manual packaging and uploading becomes a bottleneck.

### The GitOps Principle Applied to migasfree

Under the GitOps paradigm:

1. **Git as the single source of truth**: Every package, post-installation script, and configuration file is versioned in a Git repository.
2. **Traceability and peer review**: Any modification is processed via merge/pull requests, ensuring code review before hitting production.
3. **Automated build and publication**: Tagging a new version in Git triggers CI/CD pipelines that build the .deb/.rpm package and upload it automatically to the migasfree server.

This automation can be implemented with tools such as **GitLab CI** or **GitHub Actions**. Delving into the details of each platform is beyond the scope of this introductory part; in [Part III (Administration)](part03.md#iii-administracion) you will see how release and deployment automation fits into the full migasfree lifecycle.

\

## Methodology

Having understood packaging and distribution, it is valuable to systematize the workflow into three distinct phases:

1. **Investigate on the client**: Focus exclusively on solving the technical requirement locally on a test machine.
2. **Package the solution**: Once the local problem is resolved, abstract the solution and encapsulate it into a .deb or .rpm package.
3. **Schedule the deployment**: With the package built, focus exclusively on defining *who* receives the package and *when* via migasfree deployments.

This strict separation not only brings conceptual clarity to administrators, but also enables technical team specialization:

* **OS and application specialists**: Focus on local research, diagnosing issues, and designing solutions.
* **Packagers**: Specialize in automating, building, and integrating solutions into standard packages.
* **Release managers / Server administrators**: Manage rollout strategies, pilot testing, and progressive fleet deployments.

## Conclusion

Although **packaging SCIs** requires an initial effort, the long-term benefits are substantial:

* You will have more stable systems.
* It allows you to track and control changes systematically.
* And you will significantly improve incident resolution times.

### Benefits of Creating Configuration Packages

* Configuration remains encapsulated.
* Configurations can be easily rolled back.
* Facilitates pre-deployment testing.
* Facilitates secure configuration distribution.
* Provides integrity against configuration drift and change.

### Disadvantages of Configuration Packaging

* Requires higher initial effort than quick scripting, as packaging rules and standards must be followed.

### Benefits of Using migasfree

Using *migasfree* for *Release Management* enables you to:

* Control who receives changes and from what moment.
* Maintain centralized auditing:
  * Computer inventory.
    * Hardware.
    * Software (current and historical).
  * Change inventory.
  * and several other capabilities that will be unveiled in subsequent chapters.

In this chapter we performed the entire process manually on purpose: building the package locally, uploading it via CLI, and assigning it in the web console.

However, this manual workflow is only the starting point. In real production environments—such as the Zaragoza City Council or the [Vitalinux](https://docs.vitalinux.educa.aragon.es/info/) project—the **ideal goal** is to **completely automate this cycle through Continuous Integration and Continuous Deployment (CI/CD) pipelines**. In this way, every commit or tag in the code repository automatically triggers package compilation and publication in migasfree.

The image *A change request in Vitalinux using Redmine* illustrates a **real request** to [Vitalinux Support](https://soporte.vitalinux.educa.aragon.es/projects/vitallinux-dga-soporte) along with its tracking and resolution using CI/CD. It serves as an example of how project management and issue tracking systems operate in practice. In this specific case, a wallpaper change was requested for all computers at Tenerías Early Childhood and Primary School in Zaragoza to appear on desktops only between November 24th and 29th. The [change](https://gitlab.vitalinux.educa.aragon.es/vitalinux-devops/vx-dga-l-conf-centro-ceiptenerias/-/commit/3b16cec8e46a1fa0e54d4a4a57fdeb85c5451e26) requested by Daniel was made to package [vx-dga-l-conf-centro-ceiptenerias](https://gitlab.vitalinux.educa.aragon.es/vitalinux-devops/vx-dga-l-conf-centro-ceiptenerias), and was tagged as version 1.0-18 on November 20, 2024 by Arturo. Upon doing so, [CI/CD](https://gitlab.vitalinux.educa.aragon.es/vitalinux-devops/vx-dga-l-conf-centro-ceiptenerias/-/blob/1.0-18/.gitlab-ci.yml) automatically built the package for both vitalinux18 and vitalinux3x, ultimately releasing these packages into the migasfree deployments named repo-ceip-tenerias-zaragoza. You can see the jobs performed by GitLab CI/CD [here](https://gitlab.vitalinux.educa.aragon.es/vitalinux-devops/vx-dga-l-conf-centro-ceiptenerias/-/pipelines/3729).

I would like to highlight that Arturo **focused exclusively** on the core technical task: updating the wallpaper file and tagging the version. Everything else was automated.

Although I personally know the Vitalinux technicians and we regularly exchange experiences, I chose this example because it is publicly accessible, transparent, and illustrates the power of combining project management, Git, CI/CD, and migasfree.

If you want to explore Vitalinux packages, visit this [link](https://gitlab.vitalinux.educa.aragon.es/explore).

With the packaging cycle mastered, in the next chapter we will examine how client computers interact with the server during synchronization.

# Evolution

> > Freedom is not the ability to choose from among a few imposed options, but rather having control over your own life.

In the previous chapter, we put into practice the fundamentals of Software Configuration Management (SCM) by creating and deploying our first configuration package: acme-test-files.

However, administering a fleet of computers in the real world poses a fundamental double challenge:

1. **Evolution of the base distribution**: The operating system (Debian, Ubuntu, Red Hat…) releases security updates, package changes, and new software versions continuously.
2. **Evolution of the organization**: Your entity needs to adapt policies, change corporate servers, customize applications, and deploy internal developments at its own pace.

The major dilemma in systems engineering lies in how to make both worlds coexist without colliding—that is, how to maintain corporate customizations without breaking operating system updates or having a distribution update overwrite our custom configuration files.

In this chapter, you will learn how to solve this equation using the **packaging diversion** technique (DPKG diversions), packaging the configuration of migasfree-client itself into acme-migasfree-client, and establishing the continuous evolution workflow that unites migasfree, MGI, and MCS.

All commands in this chapter will be executed in the `VM-001` virtual machine as the `root` user.

## Investigating migasfree-client

Let us first inspect the migasfree client configuration file in `/etc/migasfree.conf`:

> ```bash
> less /etc/migasfree.conf
> ```

> ```text
> [client]
> # Computer_Name = mci-builder
> Project = FWM
> Server = migasfree.acme.com
> ```

We see that only the project and server are configured.

Now let us see which package owns this file:

> ```bash
> dpkg-query -S /etc/migasfree.conf
> ```

> ```text
> dpkg-query: no path found matching pattern /etc/migasfree.conf
> ```

No package installed it; it was created on the fly during the manual configuration process in Chapter 5.

> #### NOTE
> **How does dpkg-query respond when a file does belong to a package?**

> If we had queried for a file registered in the package manager database (for instance, `/etc/adduser.conf`), `dpkg-query` would have returned:

> ```text
> $ dpkg-query -S /etc/adduser.conf
> adduser: /etc/adduser.conf
> ```

> This indicates that `/etc/adduser.conf` belongs to package adduser.

> Conversely, returning the message `no path found matching pattern` confirms that the file is not managed by the packaging system, leaving it exposed to overwriting or accidental modification without auditability.

Next, we will configure this file using Debian packaging.

> #### NOTE
> In version 4 of migasfree-client, `/etc/migasfree.conf` did belong to the package `migasfree-client`. However, from version 5 onwards, this file is not included in the package in order to facilitate its customization via dedicated corporate packages.

## acme-migasfree-client

Just as you did with `acme-test-files` in Chapter 7, you can use the example package `acme-migasfree-client` available in the repository.

In the `VM-001` virtual machine, navigate to the `~/fun-with-migasfree-examples` directory.

> > #### NOTE
> > If you have not downloaded fun-with-migasfree-examples yet, execute the following command:

> > > ```bash
> > > wget https://github.com/migasfree/fun-with-migasfree-examples/archive/master.zip
> > > unzip master.zip
> > > cd fun-with-migasfree-examples-master
> > > ```
> ```bash
> cd ~/fun-with-migasfree-examples-master
> ```

Enter the `acme-migasfree-client` directory and inspect its content:

> ```bash
> cd acme-migasfree-client
> ls -la
> ```

> ```text
> total 4
> drwxrwxr-x 5 alberto alberto 4096 jun 18 20:54 .
> drwxrwxr-x 4 alberto alberto 4096 jun 18 21:04 ..
> drwxrwxr-x 3 alberto alberto 4096 jun 18 20:54 debian
> drwxrwxr-x 3 alberto alberto 4096 jun 18 20:54 usr
> ```

### Metadata

Inspect the `debian` directory. This directory contains the package metadata:

* The `control` file consists of a set of fields, represented in a common format, that allow the package management system to understand the package metadata and manage it properly. You can consult the [debian-policy](http://www.debian.org/doc/debian-policy/ch-controlfields.html) to explore the full set of `control data`.

* The `changelog` file contains version history and release notes in a strict standardized format.
* The `copyright` file contains information regarding licensing, copyright holders, and redistribution terms.
* The `rules` file contains the executable rules (Makefile) used to compile and build the package.
* The `install` file contains the list of files to be placed in their target filesystem locations upon installation.

Now that you understand these files, customize them by replacing placeholder metadata with your organization’s information.

> #### NOTE
> To learn more about Debian packaging, you can consult the [Debian New Maintainers’ Guide](http://www.debian.org/doc/manuals/maint-guide/index.es.html).
> #### NOTE
> On `rpm` packaging systems (such as Red Hat or Fedora), package metadata is specified in a single file called `SPEC`. To delve deeper into **rpm** package creation, you can refer to [rpm.org](http://www.rpm.org/) and the [Fedora Project documentation](https://docs.fedoraproject.org/en-US/packaging-guidelines/).

### Scripts

Now inspect the `postinst` and `prerm` maintainer scripts. Their names indicate when they execute during the package lifecycle:

* `postinst` immediately after package installation.
* `prerm` immediately before package removal.

Inspect the content of `postinst` and notice that it calls `dpkg-divert` to divert `/etc/migasfree.conf`.

The diversion instructs the distribution package manager (`dpkg`) to redirect any access, update, or installation targeting `/etc/migasfree.conf` towards an alternative path (e.g., `/etc/migasfree.conf.orig`).

This makes `dpkg-divert` the **perfect coexistence mechanism**:

* It allows the upstream distribution to keep updating packages and applying security patches without throwing conflicts.
* It ensures that our corporate customizations are never overwritten during operating system upgrades.
* If we uninstall the corporate package in the future, the `prerm` script removes the diversion, cleanly restoring the original configuration file.

Thus, the configuration file `/etc/migasfree.conf` becomes governed exclusively by our corporate package.

> #### NOTE
> **A universal pattern for any application**: The packaging and diversion technique demonstrated here with `migasfree-client` applies identically to any other software configuration (Apache, SSH, LibreOffice, GIMP, pam.d, etc.).

> #### NOTE
> **Is there an equivalent to dpkg-divert in RPM systems (Red Hat, Fedora, SUSE)?**

> In the RPM ecosystem, **there is no native command or database register equivalent to dpkg-divert**.

> To achieve a similar effect on RPM-based distributions, administrators rely on alternative strategies:

> * **Modular configuration directories (\*drop-in\* or \`\`.d\`\`)**: The modern standard in systemd, sshd, and sudoers (e.g., /etc/sudoers.d/), allowing corporate files to be added without touching base files.
> * **Emulation via \*scriptlets\* in the \`\`SPEC\`\` file**: Renaming and backing up files in `%pre` and restoring them in `%postun`.
> * **The \`\`alternatives\`\` system**: Manages dynamic symbolic links when multiple implementations of the same command or file coexist.

Now modify the file `usr/share/divert/etc/migasfree.conf` with your organization’s settings:

> ```bash
> cat <<EOF > usr/share/divert/etc/migasfree.conf
> [client]
> Project = FWM
> Server = migasfree.acme.com
> EOF
> ```

Now build the package:

> ```bash
> /usr/bin/debuild --no-tgz-check -us -uc
> ```

With this, you will have a package that configures the migasfree client for your organization.

> ```bash
> sudo apt install ../acme-migasfree-client_1.0_all.deb
> ```

Notice that upon installing the package, you are notified that the diversion is added.

> ```text
> Adding 'diversion of /etc/migasfree.conf to /etc/migasfree.conf.orig by acme-migasfree-client'
> ```

Verify that the `Server` and `Project` settings are correct.

> ```bash
> cat /etc/migasfree.conf
> ```

Also verify that the file now belongs to package `acme-migasfree-client` using `dpkg-query -S`:

> ```bash
> dpkg -S /etc/migasfree.conf
> ```

> ```text
> diversion by acme-migasfree-client from: /etc/migasfree.conf
> diversion by acme-migasfree-client to: /etc/migasfree.conf.orig
> ```

Upload the package to our migasfree server to make it available for deployment:

> ```bash
> sudo migasfree upload -f acme-migasfree-client_1.0_all.deb
> ```
* Enter the username and password for the migasfree web console.
* Project: FWM
* Store: acme

## Deployment

We will now instruct the system that all computers in the **FWM** project must install the `acme-migasfree-client` package.

Navigate to **Release > Deployments** in the migasfree web console. Edit the deployment corresponding to your project.

Add package `acme-migasfree-client_1.0_all.deb` to available packages.

In packages to install, add the package name `acme-migasfree-client`.

Save the changes.

## Continuous Evolution

At this point, we have created a new corporate configuration and deployed it to machines in production.

migasfree resolves this challenge through a **two-speed continuous evolution architecture**:

1. **Fast speed: Dynamic live evolution (migasfree)** Production machines receive packages, updates, and configuration adjustments on the fly via client synchronization, without requiring reinstallation.
2. **Consolidation speed: Cold baseline evolution (MGI + MCS)** Over time, accumulating too many post-deployment packages on a base master image increases installation time on new machines.

   To prevent this degradation, the administrator periodically consolidates successful deployments directly into the base template (`project-templates`), creating a new release in MGI (e.g., Release 1.1).

When promoting **Release 1.1** in MGI from the web console under **Master Images > Releases**, newly provisioned machines cloned with MCS will already incorporate all updates natively.

This circular workflow closes the Software Configuration Management lifecycle: fast agile evolution on the fleet via migasfree, consolidated periodically into the master baseline via MGI.

## Summary

In this chapter, we explored in depth the customization and ongoing evolution of systems:

* **Investigate file ownership**: Use `dpkg-query -S` to identify whether a configuration file belongs to a package.
* **Protect configurations via diversions (DPKG Diversions)**: Use `dpkg-divert` to preserve corporate adjustments across distribution upgrades.
* **Customize migasfree client configuration**: Create and build a dedicated corporate package (`acme-migasfree-client`).
* **Distribute corporate configuration**: Upload the package to the migasfree server and schedule its deployment.
* **Evolve the base system in MGI**: Create a new Master Image release to consolidate changes for future MCS provisioning.

With this, we conclude **Part II: Getting Started**.

Throughout this part, you moved from theory to practice: deploying a server in Docker Swarm, provisioning machines with MCS, and managing configuration lifecycle through packaging.

With this solid foundation, you are ready to delve into **Part III: Administration**, where we will examine the architectural components of migasfree in rigorous detail.

Congratulations and thank you for making it this far! Take a breather, and let us continue.

# III. Administration

After establishing the theoretical foundations of SCM in Part I and deploying a laboratory environment in Part II, you now have the necessary basis and a clear vision of migasfree. The time has come to make the leap into the operational arena. In this third part, we will focus entirely on the **how**: we will explore in depth the operation, administration, and daily use of the system in real production scenarios.

#### NOTE
**Scaling up: from laboratory to real architecture**

In Part II we used a simplified test environment so that you could experiment immediately. From this point on, we leave the simplifications behind: we will delve into the formal architecture of migasfree v5 governed by microservices, mTLS cryptographic security, robust relational databases, and orchestration with Docker Swarm. Buckle up, because we are entering a whole new dimension.

We will start by examining the server architecture and the infrastructure orchestration with Docker Swarm (`migasfree-swarm`), analyzing in detail the services that make up the migasfree v5 *stack* (proxy, core, manager, database, datastore, PMS, tunnels, etc.).

Before diving into the details, remember that this step marks the definitive transition from the experimental lab to a robust production infrastructure, where each component must be operated and monitored using best practices.

Next, we will delve into the heart of centralized management: the administration web console. You will learn to model configuration through attributes, singularities, and formulas, to govern peripherals and printers, and to structure projects, repositories, and declarative deployment policies. You will complete the modeling by defining the base system with **Master Images** (MGI) and their build engines.

From the client machines’ perspective, we will break down the components that make client convergence possible: the `migasfree-client` synchronization engine, secure remote access through `migasfree-agent`, and the self-service catalog for the end user with `migasfree-play`. Likewise, we will address the management of heterogeneous client groups by integrating the Windows environment (with `windows-package-tool` and `lshw-windows-emulator`) and the massive deployment of the base system with the **MCS** cloning system.

We will complete this section by examining the auditing, querying, and analysis techniques for the data and inventory collected by the **Data** module.

To make reading easier, the content is divided into **three blocks** of topics:

* **A. Server**: server architecture and Docker Swarm orchestration.
* **B. Modeling**: web administration console and declarative configuration modeling.
* **C. Client**: workstations, heterogeneous fleet management, and fleet telemetry.

This **Administration** part is conceived as your continuous reference manual. I suggest approaching it with patience and the console open: proceed step by step, experiment with each concept, and you will master the platform, making migasfree the automation engine of your organization.

Go ahead, make yourself at home!

# A. Server

You have left the lab behind and now enter the true engine room of migasfree. This first block of Part III is dedicated entirely to **server infrastructure**: the physical and logical foundation upon which the entire system rests.

Across two chapters you will explore the formal architecture of migasfree v5 and the mechanisms that keep it running:

* [Chapter 9 (Infrastructure)](chapter09.md#infraestructura): orchestration with **Docker Swarm**, HTTPS and mTLS certificate management, and service lifecycle governance using the `migasfree-swarm` tool.
* [Chapter 10 (Stack)](chapter10.md#stack): a monograph on the services comprising the migasfree v5 stack (proxy, core, manager, database, datastore, PMS, tunnels, etc.), detailing their ports, administration consoles, and diagnostic techniques.

By the end of this block, you will understand how each piece fits into the cluster and the role it plays in the lifecycle of packages and configurations. With that foundation in place, we can proceed to the next phase: the command center where the entire organization is modeled and governed.

# Infrastructure

> > A complex system that works is invariably found to have evolved from a simple system that worked.

Having established the conceptual foundations of SCM in Part I and experienced practical hands-on workflows in Part II, we now transition to the rigorous study of the server architecture supporting the entire system in production environments.

In this chapter you will examine the overall architecture of the migasfree server, the cluster orchestration model with Docker Swarm, and operational management using the `migasfree-swarm` CLI tool.

## Docker Swarm

[Docker Swarm](https://docs.docker.com/engine/swarm/) is Docker’s native orchestration and container clustering engine. Together with [Kubernetes](https://docs.docker.com/), it represents one of the industry standards for managing containerized applications in production.

Unlike other more complex orchestration platforms like Kubernetes, Docker Swarm stands out for its operational simplicity, low memory footprint, and native integration into the Docker daemon, requiring no heavy external infrastructure.

Its core operational pillars are:

* **Manager and Worker Nodes**: *Manager* nodes govern cluster state, maintain the Raft consensus quorum, and orchestrate scheduling; *Worker* nodes exclusively execute assigned application tasks.
* **Service and Replica Declaration**: Instead of starting standalone containers, services are declared with a target state (desired number of replicas, constraints, restart policies). Docker Swarm continuously monitors the state of the swarm and replaces failed tasks automatically.
* **Overlay Networks**: Virtual, encrypted, and isolated multi-host software-defined networks that allow containers to communicate across distinct physical hosts with zero exposure to external traffic.
* **Native Secrets Management (Docker Secrets)**: A high-security mechanism that encrypts sensitive data (passwords, TLS certificates, database keys) at rest in the Raft log and mounts them in-memory (tmpfs) exclusively inside authorized containers.

The migasfree suite adopted Docker Swarm in version 5 precisely because it balances high availability, self-healing capabilities, and horizontal scalability with ease of deployment and maintenance.

## migasfree Cluster

The following diagram illustrates the general layout of nodes, internal communication channels, and storage persistence in a production migasfree cluster:

As shown in the diagram, the cluster architecture relies on three structural principles:

* **Routing and Termination at the Gateway**: The `proxy` service (HAProxy) acts as the unique entry point, managing SSL/TLS termination and intelligently routing traffic based on path and protocol to backend microservices.
* **Decoupled Persistence by Data Type**: Ephemeral data is handled in memory, relational data in dedicated PostgreSQL volumes, and static assets/repositories on a shared distributed filesystem (NFS).

In its standard topology, a migasfree cluster consists of a primary *Manager* node (which can also execute services in small environments) and one or more *Worker* nodes that scale compute, repository generation, and client traffic capacity.

> #### NOTE
> In the current suite version, the cluster topology supports single-node deployments for small-to-medium environments and multi-node clusters sharing an NFS storage backend for large enterprises.

## migasfree-swarm

Cluster lifecycle administration, stack deployments, SSL/TLS certificate issuing, and backup routines are unified under the CLI tool `migasfree-swarm`.

Invoking the command with `--help` displays the complete operational menu:

> ```bash
> sudo migasfree-swarm --help
> ```

> ```text
> Usage:
>   migasfree-swarm <command>

> Available commands:
>   deploy                 Deploy a migasfree stack
>   undeploy               Undeploy a migasfree stack
>   redeploy               Perform undeploy + deploy
>   deploy-all             Deploy all migasfree stacks
>   undeploy-all           Undeploy all migasfree stacks
>   redeploy-all           Perform undeploy + deploy for all migasfree stacks
>   consoles-dev           Enable development consoles
>   consoles-pro           Disable development consoles
>   secret                 Show the "secrets" for console access
>   config                 Configure the swarm cluster
>   pull                   Pull all images
>   url-admin-certificate  Generate a one-time URL to create a client certificate
>                          for administration console access
>   join-worker            Add a worker node to the cluster
>   leave                  Leave the Swarm cluster
>   backup                 Backup database (PostgreSQL) and datastore (Redis) dumps
>   restore                Restore database (PostgreSQL) and datastore (Redis) dumps
>   prune                  Remove dangling images from the node
>   info                   Show cluster and stack information
> ```

These commands are operationally structured into four main areas:

* **Deployment and Lifecycle**: Commands such as `deploy`, `undeploy`, `status`, and `restart` to govern stack runtime state.
* **Security and Consoles**: Commands such as `consoles-dev`, `consoles-pro`, `admin-url`, and `credentials` to manage administrative access, diagnostic portals, and mTLS certificates.
* **Topology Management**: Subcommands such as `join-worker`, `leave-worker`, and node scaling routines.
* **Maintenance and Backup**: Commands such as `backup`, `restore`, `pull`, and `prune`.

### Cluster Storage Configuration

Before deploying services for the first time, you must define the persistence backend (local filesystem or shared NFS mount):

> ```bash
> sudo migasfree-swarm config
> ```

This interactive command generates the global cluster configuration file (`cluster.conf`) where storage types, server FQDNs, and stack parameters are stored.

> #### NOTE
> **Upgrading from migasfree v4?** If you are migrating a legacy deployment, the [official migasfree migration guide](https://migasfree.org) outlines the data conversion steps prior to initial deployment.

### Stack Deployment

Once cluster storage is configured, deploying the service stack is achieved with a single command:

> ```bash
> sudo migasfree-swarm deploy
> ```

During initial deployment, the interactive wizard will prompt for the target stack name (e.g., `migasfree` or `pro`) and the server FQDN.

### System Health Monitoring

To inspect the overall health of the cluster at a glance, execute:

> ```bash
> sudo migasfree-swarm info
> ```

> ```text
> Swarm Cluster Status
> ====================
>   Status:     active
>   Node Role:  Manager
>   Nodes:      1 (1 managers)

>   Nodes Detail:
>     ID                         Hostname             Role       Status     Availability
>     yujmm05lqfzkp8dhi4434focw  server               manager    ready      active

> Deployed Stacks
> ===============
>   • pro             -> https://migasfree.acme.com
>     Services: 21/21 running
> ```

This output provides a consolidated overview divided into two functional sections:

* **Swarm Topology Status**: Displays the local node role (*Manager* or *Worker*), cluster state, and active nodes.
* **Deployed Stacks**: Lists each active stack along with the real-time replica status of all microservices (1/1 indicates a healthy service).

### Service Upgrades and Redeployment

One key advantage of the clustering model is updating services without interrupting ongoing client operations:

> ```bash
> sudo migasfree-swarm redeploy core
> ```

Docker Swarm will perform a rolling update, gradually replacing containers with new versions while health checks ensure service continuity.

### Development and Diagnostic Consoles

During maintenance or troubleshooting, you can enable auxiliary administrative web interfaces by running:

> ```bash
> sudo migasfree-swarm consoles-dev
> ```

This exposes direct debugging dashboards and extended logs for the database, cache, and reverse proxy.

### mTLS Administration

Mutual TLS (mTLS) authentication is an advanced security mechanism where both client and server authenticate each other via digital X.509 certificates.

In the migasfree v5 architecture, mTLS protects administrative web consoles and sensitive REST APIs against unauthorized access, even in hostile network environments.

> ```bash
> sudo migasfree-swarm redeploy
> ```

With mTLS active, issuing an administrator certificate requires no external CA tools:

> ```bash
> sudo migasfree-swarm url-admin-certificate
> ```

When executing this command on the *Manager* node, the interactive wizard will request:

1. **Stack**: Name of the cluster stack (for instance, `pro`).
2. **User**: Name or *Common Name* (CN) of the administrative user (e.g., `alberto`).
3. **Validity**: Certificate validity period in days (default: 365).

After entering these parameters, the tool generates a secure one-time download URL:

> ```text
> {
>   "url": "https://migasfree.dominio.org/manager/v1/public/mtls/admin-requests/a1b2c3d4..."
> }
> ```

This URL is provided to the administrator to import the PKCS#12 bundle (.p12) directly into their web browser or CLI client.

### Credentials and User Management

During stack initialization, `migasfree-swarm` automatically creates cryptographically random credentials for root system services.

To query these infrastructure credentials on the *Manager* node, execute:

> ```bash
> sudo migasfree-swarm secret
> ```

This command extracts and prints the bootstrap master credentials on the console:

#### IMPORTANT
**Principle of Least Privilege:** Master bootstrap passwords should never be shared among administrative staff.

To grant access to additional administrators, helpdesk technicians, or automated systems, create dedicated individual accounts in the migasfree web console under **Security > Users**.

### Pull and Prune

Managing local storage across cluster nodes is kept tidy via dedicated maintenance routines:

* **Proactive Image Pulling**: Pre-download container images across all nodes before performing upgrades by executing `migasfree-swarm pull`.
  > ```bash
  > sudo migasfree-swarm pull
  > ```
* **Disk Space Cleanup**: Clean up obsolete container images, build caches, and untagged volumes by running `migasfree-swarm prune`.
  > ```bash
  > sudo migasfree-swarm prune
  > ```

### Server HTTPS Certificates

The `proxy` service acts as the secure cluster gateway, terminating TLS on port 443.

Three operational modes are supported depending on organizational requirements:

* **Self-Signed (\`\`self-signed\`\`)**: Default mode for testing and isolated lab environments.
* **Automated Let’s Encrypt (\`\`auto\`\`)**: Recommended for environments with a public domain name and direct Internet access on ports 80/443.
* **Corporate Manual (\`\`manual\`\`)**: Designed for enterprises using certificates issued by their internal Corporate Public Key Infrastructure (PKI).

To apply any change to the HTTPS certificate mode, update `cluster.conf` and execute `migasfree-swarm deploy`.

> ```bash
> sudo migasfree-swarm redeploy
> ```

### Safe Infrastructure Shutdown

If you ever need to stop the entire stack while ensuring database consistency and preventing data corruption:

> ```bash
> sudo migasfree-swarm undeploy
> ```

## Scalability

When an organization expands or client workload needs to be distributed, the cluster can be horizontally scaled by adding *Worker* nodes.

For multiple nodes to share packages, repositories, and certificates, the cluster must use a shared NFS storage backend.

1. **Obtain the Join Command**: On the primary *Manager* node, execute `migasfree-swarm join-worker`.
   > ```bash
   > sudo migasfree-swarm join-worker
   > ```

   The tool will retrieve the cryptographic authorization token from the swarm.
2. **Join the New Node**: On the machine acting as a *Worker*, execute the generated join command.
   > ```bash
   > sudo docker swarm join --token SWMTKN-1-xxx... 192.168.1.100:2377
   > ```
3. **Verify Cluster Status**: From the *Manager* node, verify the newly joined node with `migasfree-swarm status`.
   > ```bash
   > sudo migasfree-swarm info
   > ```

Once joined, Docker Swarm will automatically distribute workloads and route traffic across the expanded cluster.

To cleanly remove a node from the cluster without causing service disruption, execute `migasfree-swarm leave-worker` on the worker node.

> ```bash
> sudo migasfree-swarm leave
> ```

> #### NOTE
> For detailed architecture design in multi-node enterprise environments, see Chapter 20 (High Availability).

## Operational Consoles

The server provides a unified web portal of operational consoles accessible via HTTPS.

> ```bash
> sudo migasfree-swarm consoles-dev   # Habilitar las consolas de desarrollo
> sudo migasfree-swarm consoles-pro   # Desactivarlas al finalizar la intervención
> ```

> #### NOTE
> Advanced stack monitoring (HAProxy metrics, Redis inspection, database query statistics) is detailed in [Chapter 10 (Stack)](chapter10.md#stack).

## Backups

The `migasfree-swarm` tool streamlines data backup and disaster recovery operations.

> ```bash
> sudo migasfree-swarm backup <STACK>            # Volcado estándar (migasfree.sql y migasfree.rdb)
> sudo migasfree-swarm backup <STACK> <NOMBRE>   # Volcado con nombre personalizado
> sudo migasfree-swarm restore <STACK>           # Restauración estándar
> sudo migasfree-swarm restore <STACK> <NOMBRE>  # Restauración de un volcado específico
> ```

> #### NOTE
> For the complete disaster recovery plan, see Chapter 20 (High Availability).

## Summary

In this chapter, we established the operational foundation of the server infrastructure:

* **Orchestration Architecture**: Understood the fundamentals of Docker Swarm, manager/worker roles, overlay networks, and secrets.
* **Cluster Governance with migasfree-swarm**: Mastered deployment, lifecycle, mTLS certificate, and credential management commands.
* **Security and Certificates**: Configured HTTPS certificate modes (self-signed, Let’s Encrypt, corporate manual) and administrator mTLS authentication.
* **Scalability and Continuity**: Connected and decommissioned cluster nodes and established data backup workflows.

In the next chapter, we will analyze in depth each of the individual services comprising the migasfree v5 stack.

# Stack

> > Great things are not done by impulse, but by a series of small things brought together.

Having studied cluster orchestration and lifecycle governance with Docker Swarm in the previous chapter, we now focus our attention on the structural anatomy of the services comprising the migasfree v5 platform.

True to Van Gogh’s quote, the migasfree v5 server is not a monolithic application, but a set of specialized, independent microservices working in harmony: a perimeter reverse proxy, a responsive user interface, a central business logic engine, asynchronous background workers, scheduling daemons, caching and persistence layers, multi-platform package indexers, secure tunnels, and AI integration bridges.

All these components coexist and communicate across an isolated encrypted overlay network, as detailed in the Chapter 9 cluster architecture diagram.

## Observability

Before examining each service in depth, understanding the observability mechanisms provided by the platform to monitor cluster health, diagnose bottlenecks, and inspect execution traces in real time is essential.

migasfree provides complementary observability tools across both web interfaces and the command line:

1. **The Global Status Console**: Accessible at `https://<FQDN>/status` (when auxiliary consoles are enabled via `migasfree-swarm consoles-dev`), this console provides a unified telemetry dashboard organized into three operational tabs:
   * **Services**: Displays an interactive grid of all stack microservices, showing their real-time execution status (green/red indicators), listening ports, and direct links to specialized administration consoles (Portainer, pgAdmin 4, RedisInsight, HAProxy Stats, Flower, Filebrowser, etc.).
     > 
   * **Synchronizations**: Offers real-time telemetry on incoming client synchronizations and server CPU consumption via four key indicator panels:
     - **SERVER STATUS**: Overall server operational state (e.g., `OK (Normal load)`).
     - **CORE CPU AVG**: Average CPU utilization percentage consumed by the `core` service across all instances.
     - **SAMPLING INT.**: Metrics sampling frequency in seconds.

     Accompanying these summary cards, two real-time graphs detail temporal evolution over the last hours:
     - **Synchronization Attempts**: Records incoming client sync attempts per minute, distinguishing between successful requests, queued requests, and rejections.
     - **Core CPU Load**: Displays the percentage of processor utilization consumed by the business logic engine.

     > 
   * **Database and Pgpool-II**: Provides full visibility into query response times, connection pooling efficiency, and database load via three indicator panels:
     - **GATEWAY LATENCY**: Average response time in seconds for database queries processed through the pool.
     - **DB CPU AVG**: Average CPU utilization consumed by the database engine.
     - **CLUSTER NODES**: Number of active database nodes in the cluster (primary and replicas).

     Below these summary cards, three graphs analyze performance in detail:
     - **Gateway Latency**: Temporal trend of query latency passing through the pooling layer.
     - **Database CPU Load**: Historical CPU utilization consumed by the PostgreSQL container.
     - **Load Distribution**: Illustrates the breakdown of read operations versus write transactions routed to the database backend.

     Finally, the **Cluster Status (Pgpool-II)** table audits the real-time state of each database node in the cluster:
     - **ID and HOST**: Node identifier and container hostname.
     - **ROLE**: Node role in the replication topology (`PRIMARY` for the primary read/write node, `STANDBY` for read replicas).
     - **STATUS**: Operational availability state (`ONLINE` / `OFFLINE`).
     - **CPU**: Instantaneous processor load on the node.
     - **REPLIC. LAG**: Replication lag in bytes or seconds relative to the primary node.
     - **READS, WRITES, and DB ERRORS**: Cumulative volume of read queries, write transactions, and error counts.

     > 
2. [Portainer](https://www.portainer.io/):

   Provides a complete graphical interface for Docker Swarm management, allowing you to:
   * Inspect on which swarm nodes each service replica runs and its memory/CPU consumption.
   * Stream real-time container logs with live filtering.
   * Open interactive terminal consoles inside containers for low-level diagnosis.

> 

If you prefer working from the terminal, Docker Swarm enables streaming container logs directly using `docker service logs`.

> ```bash
> docker service logs -f <STACK>_<nombre_servicio>
> ```

For example, to audit events for the `core` service or the `proxy` in real time:

> ```bash
> docker service logs -f pro_core
> docker service logs -f pro_manager
> ```

As shown, these observability mechanisms—the /status web portal, Portainer, and CLI logs—give you complete control to inspect the inner workings of every service detailed below.

## proxy

The `proxy` service is based on [HAProxy](https://www.haproxy.org/) and constitutes the single entry point and security gateway for the entire cluster.

The `proxy` service is deployed in Docker Swarm in **global mode**, running an instance on every node of the cluster.

In this way, an external load balancer can distribute incoming traffic across any cluster node, and the local HAProxy instance will intelligently route requests to the appropriate backend containers over the internal overlay network.

Proxy behavior is declaratively parameterized in `stack.conf` via variables such as `TIMEOUT_CONNECT`, `TIMEOUT_CLIENT`, and `TIMEOUT_SERVER`.

To monitor routed traffic, response times, and backend connection states in real time, HAProxy provides a dedicated metrics dashboard ([HAProxy Stats](https://www.haproxy.com/blog/exploring-the-haproxy-stats-page)):

## certbot

The `certbot` service handles obtaining, verifying, and automatically renewing SSL/TLS certificates via the ACME protocol and [Let’s Encrypt](https://letsencrypt.org/), using the [Certbot](https://certbot.eff.org/) client.

This service is deployed automatically in the cluster whenever `CERT_MODE=auto` is configured in `cluster.conf`.

> ```text
> HTTPSMODE='auto'
> ```

### Lifecycle and Automatic Renewal

1. **Challenge and Validation (HTTP-01)**: Upon deploying the stack, `certbot` requests the certificate for the domain defined in `SERVER_FQDN`, placing validation tokens in the shared storage path `/pool/acme-challenge/`.
2. **Combined Certificate Generation**: Once validated, `certbot` concatenates the private key, public certificate, and intermediate CA chain into a unified .pem bundle and saves it to `/ssl/certs/` in the shared storage.
3. **Continuous Renewal Daemon**: A background daemon checks certificate validity every 12 hours. When less than 30 days remain before expiration, it renews the certificate automatically and signals HAProxy to reload without interrupting connections.

## console

The `console` service provides the web user interface (*frontend*) of migasfree, built with the [Quasar Framework](https://vuejs.org/) (based on Vue.js) and [Vite](https://quasar.dev/).

Source code is available in the [migasfree-frontend](https://github.com/migasfree/migasfree-frontend) repository.

It is the primary interactive dashboard used by systems administrators to model configurations, inspect hardware inventories, manage deployments, and trigger remote actions.

The number of web interface instances is parameterized in `stack.conf` via the `REPLICAS_console` directive.

It is accessed directly by navigating to `https://<FQDN>/`.

Key capabilities accessible from the console include:

* **Computers**: Detailed endpoint inspection (hardware, operating system, network interfaces, assigned attributes, synchronization history).
* **Attributes and Categorization**: Definition of logical attributes, dynamic formulas, and hardware criteria to organize the fleet organically.
* **Software Policies and Deployments**: Creation of projects, software repositories, scheduled deployments, and application catalogs.
* **Direct Remote Actions**: Real-time triggering of on-demand synchronizations, SSH consoles, VNC graphical sessions, and package queries.
* **User Management and Security**: Administration of user accounts, roles, access permissions, and mTLS certificates.

These are just a few of the possibilities offered by the console; we will explore them in detail in [Chapter 11 (Console)](chapter11.md#consola).

## core

The `core` service implements the central business logic of migasfree v5 via a Django application. It is the guardian of the organization’s data model, the primary REST API, and declarative evaluation rules for package assignment to machines.

Source code is available in the [migasfree-backend](https://github.com/migasfree/migasfree-backend) repository.

The number of `core` service instances is parameterized in `stack.conf` via the `REPLICAS_core` directive.

To interact with relational persistence and asynchronous messaging, `core` connects to the `database` (PostgreSQL) and `datastore` (Redis) services.

Additionally, the `core` service allows customizing server behavior by placing custom settings in `/conf/settings.py` within the shared storage volume.

After saving changes in `settings.py`, you must restart the service by running `migasfree-swarm restart core`.

> ```bash
> sudo migasfree-swarm redeploy core
> ```

The interactive OpenAPI/Swagger schema and documentation can be explored by navigating to `https://<FQDN>/api/v1/schema/swagger-ui/`.

This REST API constitutes the central nervous system of migasfree: every console action, client synchronization, and automated CI/CD pipeline communicates through these endpoints.

> #### TIP
> For a complete practical guide with Python and Bash examples, consult [Annex 2 (REST API)](annex02-rest-api.md#anexo-api-rest).

To ensure maximum API responsiveness, `core` delegates computationally heavy or long-running tasks to the `worker` service.

## manager

The `manager` service is a reactive and asynchronous component (built with [FastAPI](https://fastapi.tiangolo.com/) and [Uvicorn](https://uvicorn.dev/)) that manages high-frequency real-time operations.

Its primary responsibilities include:

* Regulating incoming client synchronization rates and concurrency using intelligent token-bucket flow control algorithms.
* Managing the local Certificate Authority (*CA*), issuing and revoking client/admin mTLS certificates.
* Collecting real-time telemetry metrics and feeding the /status operational dashboard.
* Coordinating MGI Golden Image compilation pipelines in Docker Swarm.

Manager behavior is governed in `stack.conf` via directives such as `SYNC_CONCURRENCY_LIMIT` and `TELEMETRY_INTERVAL`.

Like `core`, its interactive API schema is accessible at `https://<FQDN>/manager/docs`.

## worker

The `worker` service executes asynchronous background tasks, powered by [Celery](https://docs.celeryq.dev/) and using Redis as its message broker.

Its core responsibilities include:

* **Inventory Processing**: Asynchronously parsing and inserting hardware/software inventories received from client synchronizations into the database.
* **Deployment Precomputation**: Periodically evaluating attribute rules and precomputing repository assignments for each computer to optimize sync latency.
* **Maintenance and Cleanup**: Purging orphan attributes, checking package checksums, and cleaning up temporary files.
* **Event and Alert Queues**: Processing notification queues and email dispatches.
* **Schema Migrations**: Executing database schema migrations upon deploying new server versions.

The number of worker instances is configured in `stack.conf` via the `REPLICAS_worker` directive.

To monitor worker activity and task queues in real time, migasfree integrates [Flower](https://flower.readthedocs.io/):

## beat

The `beat` service acts as the periodic task scheduler and cron daemon for the cluster, implemented with [Celery Beat](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html).

Unlike other components, `beat` does not execute tasks directly; it dispatches periodic events into Redis queues for `worker` instances to consume.

By architectural design, `beat` always operates as a *singleton* (a single replica) to prevent duplicate execution of scheduled jobs.

## database

The `database` service provides the relational database engine, running [PostgreSQL](https://www.postgresql.org/) 16+.

In multi-node deployments, `database` is declaratively pinned to a specific manager node using Docker Swarm placement constraints.

Connection parameters (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`) are managed automatically via Docker Secrets and `stack.conf`.

For advanced PostgreSQL administration and diagnostics, migasfree integrates [pgAdmin 4](https://www.pgadmin.org/):

Accessible directly from `https://<FQDN>/status` by clicking on the pgAdmin icon, it allows you to:

* **Explore Data Models**: Inspect the complete table hierarchy, indexes, sequences, and foreign keys.
* **Interactive Query Tool**: Execute arbitrary SQL queries, explain execution plans (EXPLAIN ANALYZE), and optimize queries.
* **Real-time Monitoring**: Supervise active sessions, locks, transaction rates, and cache hit ratios.

## pgpool

The `pgpool` service implements a middleware connection pooling layer using [Pgpool-II](https://www.pgpool.net/).

Its purpose is to dramatically optimize database performance under concurrent client workloads:

* **Connection Pooling and Reuse**: Maintains warm pools of PostgreSQL connections, eliminating TCP connection overhead for rapid API requests.
* **Rate Limiting and Protection**: Prevents sudden spikes in client traffic from exhausting database connection limits.
* **Routing and Balancing**: In multi-node setups with read replicas, intelligently routes write queries to the primary and load-balances SELECT queries across replicas.

For backend services to use this pooling layer, configure `POSTGRES_HOST=pgpool` in `stack.conf`.

## datastore

The `datastore` service provides an in-memory key-value data store powered by [Redis](https://redis.io/).

Its primary roles include:

* **Asynchronous Task Broker**: Acts as the message queue for Celery tasks dispatched to workers.
* **Cache and Precomputation**: Holds precomputed computer-to-deployment mappings and fast token caches in RAM.
* **Telemetry and Contention Queues**: Stores real-time synchronization time-series and token buckets for flow control.

Connection variables (`REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`) are configured in `stack.conf`.

For key inspection and queue debugging, migasfree integrates [RedisInsight](https://redis.io/insight/):

## datashare

The `datashare` component represents the shared filesystem volume mounted across all cluster nodes (local directory or NFS mount).

The core layout of the shared storage directory includes:

* **stack.conf**: Central stack configuration file governing replica counts, timeouts, and service parameters.
* **/ca-certificates/**: Certificate Authority (CA) certificates trusted by the cluster.
* **/conf/**: Advanced Django configuration overrides (`settings.py`).
* **/consoles/**: Persistent state and configuration data for auxiliary web consoles.
* **/dump/**: Storage target for automated logical database and cache backups.
* **/keys/**: GPG and RSA cryptographic keys used for signing repository indexes and verifying tokens.
* **/plugins/**: Custom extensions and community plugins for the server.
* **/pool/**: General-purpose public storage directory (exposed at `/pool/`).
* **/public/**: Software package repositories generated by PMS indexers (exposed at `/public/`).

To facilitate file management without requiring direct SSH access to cluster nodes, migasfree integrates [Filebrowser](https://filebrowser.org/):

## public

The `public` service is a high-performance HTTP web server based on [Nginx](https://nginx.org/).

Its responsibilities include:

* Serving package repositories generated by PMS indexers at `/public/` with high-concurrency static file optimizations.
* Distributing Master Images for cloning (at `/pool/mgi/` and `/pool/mcs/`).

The number of file server instances is parameterized in `stack.conf` via `REPLICAS_public`.

Any published asset can be verified directly in your browser at `https://<FQDN>/public/`.

## pms

The **PMS** (*Package Management System*) services form the modular package indexation layer:

* **pms-apt**: Indexer for `.deb` packages and APT repositories (Debian, Ubuntu, Linux Mint).
* **pms-yum**: Indexer for `.rpm` packages and YUM/DNF repositories (Red Hat, Fedora, Rocky, AlmaLinux, openSUSE).
* **pms-pacman**: Indexer for `.pkg.tar.zst` packages and Pacman repositories (Arch Linux, Manjaro).
* **pms-apk**: Indexer for `.apk` packages and APK repositories (Alpine Linux).
* **pms-wpt**: Package manager for Windows Package Tool. This service relies on the [windows-package-tool](https://github.com/migasfree/windows-package-tool) (WPT) package manager and the [lshw-windows-emulator](https://github.com/migasfree/lshw-windows-emulator) hardware inventory emulator, designed specifically to integrate Microsoft endpoints seamlessly into the platform. Given its importance in hybrid fleets, we will dedicate [Chapter 17 (Windows Environment)](chapter17.md#entorno-windows) exclusively to addressing its management in detail.

### Technical Role in the Platform

When an administrator uploads new software or a deployment is updated, the corresponding PMS service executes three automated tasks:

1. **Metadata Extraction**: The PMS analyzes uploaded package binaries, extracting control fields (architecture, version, dependencies, conflicts).
2. **Repository Index Generation**: Rebuilds repository metadata indexes (Packages.gz, repodata/repomd.xml, etc.).
3. **Cryptographic Signing**: Digitally signs repository indexes using the server’s GPG private key stored in /keys/.

Deployment of PMS indexers is modular: the `SERVICES_PMS` directive in `stack.conf` defines which indexers run (e.g., `SERVICES_PMS="apt yum"`).

## tunnel

The `tunnel` service implements a reverse relay server based on WebSockets and SSH, enabling on-demand bidirectional communication with client workstations behind NAT or corporate firewalls.

### Operational Architecture

1. **Persistent Secure Channel**: The `migasfree-agent` background service running on client workstations establishes a persistent outbound WebSocket connection to the server.
2. **On-Demand Switching**: When an administrator requests a remote action (SSH console, VNC desktop, on-demand synchronization) from the web console, `tunnel` routes the session securely through the established channel without requiring incoming ports on client firewalls.

Variables `REPLICAS_tunnel` and `TUNNEL_CONNECTIONS` are defined in `stack.conf`.

## mcp-server

The `mcp-server` service implements the open [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) standard developed by Anthropic, enabling Large Language Models (LLMs) and AI agents to query and interact with migasfree.

To ensure maximum infrastructure security, the MCP server operates in **read-only mode**, providing contextual read access to fleets, software catalogs, and deployments without permitting write mutations.

Variables `NETWORK_MCP` and `MCP_RO_USER` are defined in `stack.conf`.

#### NOTE
The tools, resources, and prompt templates exposed by the server are documented in Annex 3 (MCP Integration) and [Chapter 19 (Data)](chapter19.md#datos).

## Summary

In this chapter we explored the modular architecture of the migasfree v5 stack in depth:

* **Observability and Telemetry**: Real-time cluster monitoring with the /status dashboard, Portainer, and CLI logs.
* **Entry Point and Perimeter Security**: The role of `proxy` (HAProxy) and `certbot` (Let’s Encrypt / ACME).
* **Interfaces and APIs**: The `console` web dashboard (Vue/Quasar) and the `core` REST API engine (Django/DRF).
* **Background Processing**: Delegation of heavy asynchronous tasks to `worker` (Celery) and `beat`.
* **Persistence and Data**: Relational database `database` (PostgreSQL), pooling layer `pgpool` (Pgpool-II), in-memory cache `datastore` (Redis), and shared storage `datashare`.
* **Multi-platform, Tunnels, and AI**: Multi-distribution PMS indexers (APT, YUM, Pacman, APK, WPT), real-time `tunnel` relays, and `mcp-server` for AI integrations.

Thanks to this decoupled microservice design, migasfree isolates failures, scales horizontally, and ensures enterprise-grade robustness. In the next block, we will discover how to model and govern the entire organization through the web console.

Let us discover it!

# B. Modeling

With the server infrastructure deployed and understood, we now enter the command center of migasfree: the web console and the organizational modeling engine.

Across five chapters you will learn how to govern the platform from its graphical interface and conceptualize your infrastructure:

* [Chapter 11 (Console)](chapter11.md#consola): the administration web interface, its design with Quasar and Vite, interactive forms, and navigation structure.
* [Chapter 12 (Configuration)](chapter12.md#configuracion): the organizational model, projects, scopes, and the system of logical and formula attributes defining the DNA of each machine.
* [Chapter 13 (Devices)](chapter13.md#dispositivos): fleet governance, endpoints, live hardware inventory, and real-time remote actions.
* [Chapter 14 (Release)](chapter14.md#liberacion): the package deployment and scheduling engine, software stores, deployments, and package lifecycles.
* [Chapter 15 (Master Images)](chapter15.md#imagenes-maestras): the Golden Image build system (MGI), automated recipes, modular flavours, and mass deployment orchestration.

Upon completing this block, you will master the conceptual framework of systems management with migasfree and be ready to explore the client side.

# Console

> > Design is not just what it looks like and feels like. Design is how it works.

Having studied server infrastructure and the microservices stack in previous chapters, we now enter the command center of migasfree: the [administration web console](https://github.com/migasfree/migasfree-frontend).

True to Steve Jobs’ maxim, the migasfree web console is not merely an administrative frontend; it is the conceptual workspace where fleet policies are modeled, software deployments are planned, and computer lifecycles are monitored.

In this chapter we will explore the technical architecture of the web console, its visual design system, navigation hierarchy, interactive UI components, and the delegation model based on scopes and domains.

\

## Architecture

The web console (the `console` service) is a Single Page Application (SPA) developed with the Quasar framework and Vite, running natively in modern web browsers.

All communication with the server is conducted asynchronously via REST APIs against the `core` and `manager` backends, ensuring an agile, responsive user experience without full page reloads.

### Visual Identity

The migasfree graphic interface features a curated, modern design crafted to make systems administration clear, intuitive, and visually pleasant.

This design language combines elegance and dynamism through the following principles:

* **Warm Corporate Color Palette**: Utilizes a warm primary coffee/amber tone (`#8a5638`) paired with soft gradients, avoiding saturated primaries and offering a distinctive identity.
* **Glassmorphism Surfaces**: Toolbars, search bars, and floating action panels employ subtle backdrop blur effects, providing depth and visual hierarchy.
* **Purposeful Typography**: The interface combines **Dosis** for distinct brand identity headers with **Inter/Roboto** for optimal reading clarity in data tables and technical fields.
* **Fluid Micro-Interactions**: Smooth state transitions, interactive hover effects, and contextual badges provide instantaneous visual feedback.

### Accessibility

All components and color combinations in the console adhere to WCAG AA contrast standards, ensuring clarity and legibility.

The console incorporates a comprehensive **Dark Mode** system designed for low-light environments:

* In **Light Mode**, status indicators use deep vibrant backgrounds with contrasting light typography.
* In **Dark Mode**, badges adopt soft luminous pastel tones with dark typography, preventing eye fatigue while maintaining immediate scannability.

\

## Anatomy

The visual layout of the console is structured into an ergonomic shell divided into five functional areas:

### Header

The top toolbar provides immediate access to active context, universal search, alerts, and user settings:

1. **Sidebar Toggle**: A hamburger menu button allowing administrators to collapse or expand the main navigation drawer.
2. **Logo and Active Organization**: Displays the migasfree logo alongside the active organization and domain name.
3. **Universal Search**: Features a scope dropdown allowing instant global searches across computers, packages, projects, attributes, or documentation.
4. **Fullscreen Mode**: A toggle button to expand the dashboard across the entire display, ideal for NOC monitoring screens.
5. **Theme Switcher**: Enables one-click toggling between Light and Dark themes.
6. **Alert Center**: An interactive real-time notification hub categorized into two groups:
   
   * **Server Alerts** (cloud icon):
     - **Orphan packages and sets**: Packages uploaded to the server not assigned to any deployment.
     - **Unchecked notifications**: System events (such as hardware changes or new device detections) awaiting administrator review.
     - **Repositories generating**: Deployments whose indexes and repository metadata are currently being rebuilt by PMS services.
     - **Scheduled deployments**: Temporary deployments with active time schedules.
   * **Computer Alerts** (laptop icon):
     - **Computers synchronizing now**: Endpoints currently communicating with the server in real time.
     - **Delayed computers**: Machines that have exceeded their maximum scheduled synchronization interval.
     - **Unchecked faults**: Operational anomalies, hardware failures, or rule mismatches flagged for review.
     - **Unchecked errors**: Critical errors encountered during client synchronization executions.

   Clicking on any of these alerts redirects directly to the filtered view of the affected elements.
7. **User Account Menu**: A sliding drawer summarizing current user details, role permissions, and quick links to:
   * Switch interface language.
   * Set or modify active **Domain** and **Scope** working preferences.
   * Change personal account password.
   * Log out securely.

### Sidebar

The left sidebar hosts the main navigation menu. It can be collapsed into compact icon-only mode to maximize screen real estate.

The menu organizes administration functions into **five major functional blocks**:

* **Configuration**: Structural elements defining organizational behavior and fleet DNA.
  * **Platforms**
  * **Projects**
  * **Formulas**
  * **Singularities**
  * **Tag Categories**
  * **Attribute Sets**
  * **Fault Definitions**
  * **User Profiles**
  * **Groups**
  * **Domains**
  * **Scopes**
* **Devices**: Catalog and management of printers and peripherals.
  * **Manufacturers**
  * **Models**
  * **Features**
  * **Devices**
  * **Device Replacement**
  * **Connections**
  * **Device Types**
  * **Logical Devices**
  * **Drivers**
* **Release**: Software deployment, scheduling, and distribution mechanisms.
  * **Deployments**
  * **Schedules**
  * **Stores**
  * **Packages**
  * **Package Sets**
  * **Applications**
  * **Application Categories**
  * **Policies**
* **Master Images**: Golden Image lifecycle management (MGI).
  * **Configurations**
  * **Flavours**
  * **Releases**
  * **Builds**
* **Data**: Operational information, telemetry, and fleet inventory.
  * **Computers**
  * **Computer Replacement**
  * **Software Comparator**
  * **Package History**
  * **Users**
  * **Attributes**
  * **Tags**
  * **Synchronizations**
  * **Errors**
  * **Faults**
  * **Status Logs**
  * **Migrations**
  * **Messages**
  * **Notifications**

We will dedicate upcoming chapters to dissecting each of these modules in detail.

\

### Active Banner

When an administrator selects an active **Domain** or **Scope** preference from their account menu, a persistent banner appears at the top of the workspace.

### Workspace

The central canvas hosts the active loaded view. Views maintain a consistent layout comprising three navigation elements:

* **Breadcrumbs**: A hierarchical navigation trail located in the upper left corner to navigate back across sections.
* **View Header with Metrics**: Displays the section title, resource icon, and live record counts matching active filters.
* **Floating Scroll Buttons**: In long listings or detailed forms, quick buttons allow jumping directly to top or bottom.

### Footer

The bottom footer provides copyright information, links to official documentation, and the currently installed version of migasfree.

\

## Components

To guarantee a minimal learning curve and consistent user experience, the console is built upon reusable UI components.

### Dashboard

The Executive Dashboard is the welcome screen upon login. It offers a high-level operational overview:

* **Key Indicator Cards (KPIs)**: Display total counts of computers, active deployments, orphan packages, and pending alerts.
* **Interactive Donut Charts**: Break down fleet composition by platform, operating system version, project, and computer status.
* **Activity Time Series Charts**: Display daily synchronization volume and error rates over time.

### Tables and Filtering

All resource collections (computers, packages, projects, deployments) are presented in responsive data tables with advanced filtering capabilities.

The table system is powered by the following interaction mechanisms:

* **Column Quick Filters**: Each table column includes instant search inputs for rapid exact or wildcard matching.
* **Advanced Filter Panel («More Filters»)**: Clicking the funnel icon reveals a comprehensive search drawer:
  * **Global Search**: Free-text search matching multiple attributes across the dataset.
  * **Specific Dropdowns**: Selectors to filter by platform, project, domain, or computer status.
  * **Hardware and Software Technical Filters**: Direct inputs to filter by RAM size, CPU model, motherboard, MAC address, or installed packages.
  * **Date Ranges**: Interactive calendar selectors to query synchronizations or errors between specific dates.
  * **«Clear All Filters» Button**: Instantly resets all active filters and returns the view to its complete dataset.
* **Data Export**: In the top right corner of any listing, buttons allow exporting filtered data directly to CSV or JSON formats.
* **Row Actions**: Every row includes direct action buttons (edit, duplicate, delete, inspect details).
* **Batch Operations**: Selecting multiple checkboxes activates bulk actions (bulk tagging, mass deletion, deployment assignment).
* **Smart Pagination and Sorting**: Allows sorting by any column and adjusting pagination (10, 25, 50, 100 records per page).
* **Visual Status Badges**: States are represented through color-coded badges with tooltips.

### Related Data

One of the most powerful and distinctive features of the migasfree interface is its relational context navigation engine.

In any table or detail view, key elements (computers, projects, deployments, packages) feature a distinctive **related data action button**.

Clicking this button queries the backend in real time and opens a floating context drawer containing:

1. **Links and Counters to Related Data**: Shows a categorized list of all entities connected to the item (e.g., packages contained in a deployment, computers belonging to a project, synchronizations of a specific endpoint).
2. **Direct External Actions**: Action buttons to interact with third-party tools or trigger custom scripts (SSH terminal, VNC session, Redmine ticket link, monitoring graph).

#### NOTE
External actions are fully declarative and customizable via `settings.py`, allowing administrators to integrate migasfree with their existing enterprise toolchain.

### Detail Views

When editing or inspecting any item, information is structured across logical tabs (General, Attributes, Software, History, Network).

Forms integrate specialized interactive controls such as **dual-list transfer pickers** (for assigning packages or attributes), syntax-highlighted code editors, and reactive dropdowns.

At the bottom of every form, the action bar provides a comprehensive set of operations:

* **Save**: Applies changes and returns immediately to the main table listing.
* **Save and continue editing**: Persists modifications while keeping the form open for further work.
* **Save and add another**: Saves the current record and immediately clears the form to create a new one.
* **Delete**: Action button with a confirmation modal dialog to prevent accidental deletion.

\

## Context

One of the biggest challenges in administering large enterprise fleets is multi-tenancy and delegated administration across multiple departments or physical sites.

* **Domains**: Represent independent organizational divisions (e.g., City Council, Education, Health, Police).
* **Scopes**: Represent physical or logical subdivisions within a domain (e.g., Headquarters, District North, Library B).

When a technical administrator operates under a specific domain or scope preference, the entire console automatically filters all views, tables, deployments, and computers to match that context without manual query construction.

## Summary

In this chapter we explored the **administration web console** in depth:

* **Modern Architecture**: A responsive SPA based on Vue 3 and Quasar, communicating via REST APIs with backend services.
* **Curated Visual Identity**: Warm color palette, glassmorphism translucencies, WCAG AA accessibility, and full Light/Dark mode support.
* **Ergonomic Navigation**: Top header with universal search, alert center, collapsible sidebar, and breadcrumb trails.
* **Consistent UI Patterns**: Executive dashboard, tables with multi-criteria filtering, relational context drawers, and standardized detail forms.
* **Delegated Administration**: Seamless multi-tenant segmentation via active domains and scopes.

With the console controls fully mastered, in the next chapter we will dive into **modeling the organization**: projects, formulas, and attributes.

Let us model our fleet!

# Configuration

> > Style is a way to say who you are without having to speak.

Having explored the design and navigation of the web console in the previous chapter, the time has come to step onto the bridge: the migasfree **Configuration** module.

A key distinction before starting: in migasfree, the **Configuration** module is not about server internal infrastructure settings (such as network ports, databases, or certificates), but about **the declarative rules with which you decide to classify, govern, and distribute software across your fleet of computers**.

Effective administration of thousands of endpoints is not about intervening machine by machine or blindly running scripts. It is founded upon modeling the technical and organizational reality of your institution: knowing what hardware each workstation has, what location or department it belongs to, and what health status it exhibits. With that information, the server dynamically segments the fleet in real time and automatically determines which packages and policies apply to each machine.

Throughout this chapter we will examine each of these components in detail:

* Defining **Platforms and Projects** as the foundations of software delivery.
* Extracting dynamic attributes using **Formulas and Singularities**.
* Taxonomic and logical classification with **Tag Categories** and **Attribute Sets**.
* Proactively detecting anomalies using **Fault Definitions**.
* Governance and delegation of authority through **User Profiles**, **Groups**, **Domains**, and **Scopes**.

\

## Overview

The heart of migasfree is **declarative attribute-based management**. Instead of relying on static inventories or fixed IP addresses, each machine periodically evaluates its own state and communicates a collection of identifying attributes (such as architecture, memory, CPU model, department, or subnet) to the server.

From this information, the server deterministically deduces which repositories, packages, peripheral drivers, and policies must be applied to each machine.

The following diagram summarizes the flow of this synchronization lifecycle:

1. **Synchronization**: The client initiates communication with the server periodically, at system boot, user login, or on demand.
2. **Formulas**: The server responds by sending active applicable formulas—that is, Python or Bash scripts responsible for inspecting the system.
3. **Execution**: The client executes the formula code locally; values emitted to standard output form the machine’s attributes.
4. **Attributes**: The client submits these attributes back to the server, describing hardware, network, and operational context.
5. **Evaluation**: The server evaluates received attributes, resolves logical sets, and determines exactly which software, packages, and configurations match the machine.
6. **Repositories**: The server delivers repository sources, installation/removal actions, and directives the client must execute to converge to the Desired State.

The **Configuration** module provides the tools to define the rules of this lifecycle: what code the server dispatches to endpoints, how results are classified, and what privileges administrators possess.

Below, we analyze each component of this module individually.

\

## Platforms

*Configuration > Platforms*

A **Platform** defines the operating system family running on each computer in the fleet (such as `Linux`, `Windows`, or `Darwin` for macOS).

To ensure consistent and unambiguous naming, migasfree directly uses the value returned by the standard Python function `platform.system()` when executed on the client machine.

In the data model, a platform is defined by a single field:

* **Name**: Platform identifying string.

### Platform Auto-registration

During synchronization, the client reports its platform to the server. Server behavior upon encountering unregistered platforms is controlled by `MIGASFREE_AUTOREGISTER`: if enabled (default), the server automatically registers the new platform and generates an internal notification with the source IP; if disabled, it rejects the request with HTTP 403 Forbidden until an administrator creates it manually under **Configuration > Platforms** or authorized credentials are used.

\

## Projects

*Configuration > Projects*

A **Project** corresponds to a **specific distribution and version** of an operating system (such as *Debian 13 (Trixie)*, *Ubuntu 24.04 (Noble)*, or *Windows 11*), customized, packaged, and maintained by the organization.

It constitutes the **fundamental grouping unit** of the fleet: every computer registered in migasfree belongs strictly to a single project at any given moment, determining its base software channels and native package manager.

Indeed, the absolute minimum required in `/etc/migasfree.conf` for a client to join the system is configuring **the server FQDN** and **the project** it belongs to. With these two parameters, the client can initiate communication, request mTLS certificates, and begin receiving directives.

### Project Strategy and Lifecycle

A common mistake when starting with migasfree is creating separate projects for each department, building, or classroom (for instance, `PROJECT-ACCOUNTING` or `PROJECT-ROOM1`). This unnecessarily multiplies technical complexity and the number of repositories to maintain.

The architectural best practice is **to keep the number of Projects to the absolute minimum** (ideally one per base OS version, such as `debian-13` or `Oracle-linux-10`). Differentiation by departments, rooms, or roles should not be done by creating distinct projects, but managed dynamically via **Attributes** and **Formulas**.

Furthermore, project lifecycles should strictly mirror upstream distribution support roadmaps (LTS / stable releases), planning progressive migrations when versions reach End-of-Life.

### Fields

When creating or editing a project in the web console, the following fields are configured:

* **Platform**: Operating system platform the project belongs to (e.g., `Linux`).
* **Name**: Descriptive project distribution name (e.g., `AZLinux-22`, `Debian-13`).
* **Packaging System**: Native package manager used (`deb`, `rpm`, `pacman`, `apk`, `wpt`).
* **Architecture**: Target binary CPU architecture (`amd64`, `arm64`, `x86_64`, etc.).
* **Auto register computers**: Allows newly synchronizing computers to automatically register in the database under this project without prior administrator approval.

### Creation from Templates

In addition to manual field-by-field creation, the web console provides the **Add from Template** action button. This capability simplifies initial setup by connecting the server to the [project-templates](https://github.com/migasfree/project-templates) ecosystem.

Administrators can import templates from two origins:

* **Remote Catalog**: Official public GitHub repository managed by the migasfree community, offering production-ready templates for Debian, Ubuntu, Rocky Linux, Alpine, and Windows.
* **Local Catalog**: Private corporate or experimental templates stored locally in `/templates/` within shared storage.

Selecting a template and naming the project automatically triggers the server to:

1. Create the **Project** with its platform, package manager, and architecture pre-configured.
2. Generate the associated **MGI Configuration** (partition schemes, base scripts, and modular flavours).
3. Import the pre-configured software layout: **stores**, **deployments**, and **application catalog**.

This allows deploying a robust, functional software distribution in seconds.

### Physical Structure on the Server

When creating a project, the backend automatically creates its storage tree in `/public/` and initializes GPG cryptographic signing keys in `/keys/`.

If a project is deleted from the console, the server removes its database metadata while preserving physical packages in shared storage to prevent accidental data loss.

### Migration Traceability

When an endpoint upgrades its base operating system (for example, migrating from `AZLinux-20` to `AZLinux-22`), the client updates its project assignment in `/etc/migasfree.conf`.

The server detects the project change, updates the computer’s record, and logs a permanent entry in its **Migration History**, recording the timestamp and source/target projects.

\

## Formulas

*Configuration > Formulas*

In migasfree, a [Formula](annex05-glossary.md#term-Formula) is the rule or mechanism responsible for extracting system information and generating **dynamic attributes** on client machines.

As a migasfree administrator, one of your primary strategic tasks will be designing and maintaining the formulas that define the technological and organizational DNA of your fleet.

Technically, a formula is a script (in Python or Bash) stored centrally on the server and dispatched to client computers during each synchronization.

#### NOTE
A **formula** is the *extraction rule*; the **attribute** is the *extracted runtime value*.

### Fields

* **Name**: Descriptive formula name (e.g., `MACHINE_CHASSIS_TYPE`).
* **Prefix**: Alphanumeric prefix of exactly three uppercase characters (e.g., `HW_`, `NET_`, `OS_`) prepended to all attributes emitted by the formula.
* **Enabled**: If unchecked, the server will not dispatch this formula to client machines.
* **Programming Language**: Interpreter executing the script (`Python` or `Bash`).
* **Code**: Script instructions executed on the client machine.
* **Class**: Determines the processing mode applied to the script’s output:
  1. **Normal**: Standard output produces a single value (or single line).

     **Composite**: Standard output generates multiple independent attributes separated by lines or delimiters.

     **Projects**: Specific projects where this formula is active.
     ```python
     import platform
     print(platform.node())
     ```

     Dynamic Attribute Prefixing
  2. The prefix defined in the formula is automatically prepended to the emitted value. For example, if a formula with prefix `NET_` outputs `VLAN-100`, the server registers the attribute `NET_VLAN-100`.

     This naming convention prevents collisions, structures the attribute catalog into clear namespaces, and makes deployment rules self-documenting.
     ```text
     8086:a706~Host bridge: Intel Corporation Device a706 ,
     8086:a70d~PCI bridge: Intel Corporation Device a70d ,
     8086:a7a0~VGA compatible controller: Intel Corporation Device a7a0 (rev 04) ,
     8086:a71d~Signal processing controller: Intel Corporation Device a71d ,
     8086:a74d~PCI bridge: Intel Corporation Device a74d ,
     8086:a73d~PCI bridge: Intel Corporation Device a73d ,
     8086:a76e~PCI bridge: Intel Corporation Device a76e ,
     10de:28a0~VGA compatible controller: NVIDIA Corporation Device 28a0 (rev a1)
     ...
     ```

     Singularities
  3. *Configuration > Singularities*
     * A **Singularity** is a specialized formula whose exclusive purpose is calculating the unique, immutable identity fingerprint of each computer in the fleet.
     * In large fleets, identifying machines by IP address, MAC address, or hostname is fragile: network cards are swapped, USB adapters are shared, and hostnames can collide.
     * A singularity evaluates multiple persistent hardware parameters (motherboard UUID, CPU serial, chassis DMI data) and combines them into an immutable unique identifier (such as `CID-4821`).

     Fields
  4. The configuration fields of a singularity match those of standard formulas (Name, Prefix, Language, Code, Projects).
  5. The Identity Algorithm
     ```python
     import json

     # Hardcoded example to illustrate the expected format
     interfaces = [
         {"value": "192.168.1.50", "description": "Ethernet Cableado"},
         {"value": "10.0.5.20", "description": "Wi-Fi Corporativo"}
     ]
     print(json.dumps(interfaces))
     ```

     The standard singularity algorithm evaluates hardware properties in strict priority order:

### 1. Reads DMI/SMBIOS System UUID (`/sys/class/dmi/id/product_uuid`).

En un entorno de producción, las fórmulas responden a una doble necesidad operativa:

1. **Segmentar el parque**: Distribuir software, políticas y configuraciones de forma selectiva
   según las características del puesto (hardware, topología de red o identidad del usuario).
2. This ensures that even if a computer is formatted, renamed, or moved across subnets, migasfree recognizes it as the exact same machine.

Tag Categories

* *Configuration > Tag Categories*
* A **Tag Category** groups and organizes static, manually assigned labels (**Tags**) attached to computers by administrators.
* While formulas generate dynamic attributes automatically based on technical metrics, tags represent administrative metadata (such as organizational role, assigned user, or special status).

### Taxonomic Organization

Creating categories (such as `Department`, `Floor`, or `VIP User`) enforces taxonomic consistency across administrative teams.

* Fields
* **Name**: Category title (e.g., `Department`).

\

## **Description**: Functional purpose of the category.

**Prefix**: Prefix automatically added to all tags created under this category (e.g., `DEP_`).

**Multivalued**: If enabled (`True`), a machine can hold multiple tags from this category simultaneously; if disabled (`False`), assigning a new tag automatically replaces any prior tag from this category.

**Icon and Color**: Visual styling used in tables and computer detail views.

### Fields

* **Projects**: Target projects where this category is available.
* Attribute Sets
* *Configuration > Attribute Sets*
* An **Attribute Set** is a composite logical rule that groups multiple attributes using boolean logic (inclusion and exclusion).
* Attribute sets allow defining sophisticated targeting criteria for software deployments without having to assign individual attributes repeatedly.
* Set vs. Tag: Architectural Difference
* **Tags (manual and static)**: Require administrator intervention to assign or unassign on each machine.
* **Attribute Sets (automatic and dynamic)**: Evaluated by the server on the fly based on inclusion and exclusion rules.

Therefore, whenever grouping criteria can be inferred from existing attributes, creating an **Attribute Set** is the recommended best practice.

\

## **Name**: Set name (e.g., `SET-ALL-SYSTEMS`, `SET-LAPTOPS-HQ`).

**Description**: Functional explanation of the set’s purpose.

**Enabled**: Toggles active evaluation of the set.

**Included Attributes**: List of attributes required to belong to the set (ALL included attributes must be present).

### Fields

* **Excluded Attributes**: Attributes whose presence disqualifies a computer from belonging to the set.
* **Geographical Coordinates**: Optional latitude and longitude for map visualization.
* Topological Resolution and Circular Dependency Prevention
* An attribute set can include or exclude attributes generated by other sets.

### To process nested sets unambiguously, the migasfree backend employs a Topological Sorter algorithm:

Analyzes the Directed Acyclic Graph (DAG) of all attribute sets.

```text
usage: migasfree tags [-h] (-g | -s [TAG ...] | -c [TAG ...])

options:
  -h, --help            show this help message and exit
  -g, --get             Obtener etiquetas del servidor (formato JSON)
  -s, --set [TAG ...]   Establecer etiquetas en el servidor
  -c, --communicate [TAG ...]
                        Comunicar etiquetas al servidor
```

Determines the optimal evaluation order so that subsets are evaluated before dependent supersets.

* Incorporates circular dependency detection: if an administrator creates a loop (Set A includes Set B, which includes Set A), the backend rejects the change and raises a validation error.
* Practical Example: Dynamic Classroom Grouping
* Imagine managing software in a computer lab (Classroom 3), where student computers need specific software but the teacher’s machine requires specialized tools:

\

## **Create Set**: Create set `SET-CLASSROOM-3`.

**Included Attributes**: Add the classroom location attribute `LOC-ROOM-03`.

**Excluded Attributes**: Exclude the teacher workstation identifier `ROLE-TEACHER`.

Any deployment targeting `SET-CLASSROOM-3` will automatically reach all student workstations in that room while sparing the teacher’s PC.

### Fault Definitions

*Configuration > Fault Definitions*

* Modern systems management requires transitioning from a reactive troubleshooting model to a proactive, automated maintenance model.
* A **Fault Definition** is a diagnostic script dispatched to client computers to test for silent system degradation, misconfigurations, or impending hardware issues.

*Fault notification in the alert center*

### Fields

* When to use Attribute Sets vs. Tags?
* Although both tags and attribute sets group computers, their operational philosophy differs:
* **Tags (manual and static)**: Require administrator intervention to assign or unassign on each machine.
* **Attribute Sets (automatic and dynamic)**: Evaluated dynamically by the server based on boolean logic.
* Therefore, whenever grouping criteria can be inferred from existing attributes, creating an **Attribute Set** is the recommended best practice.
* **Name**: Name of the attribute set (e.g., `SET-ALL-SYSTEMS`).

### **Description**: Functional explanation of the set’s purpose.

**Enabled**: Toggles active evaluation of the set.

**Included Attributes**: List of attributes required to belong to the set.

1. **Excluded Attributes**: Attributes whose presence disqualifies a machine.
2. **Geographical Coordinates**: Optional latitude and longitude for map visualization.
3. Topological Resolution and Circular Dependency Prevention

### An attribute set can include or exclude attributes generated by other sets.

To process nested sets unambiguously, the migasfree backend:

1. Analyzes the Directed Acyclic Graph (DAG) of all attribute sets.
2. Determines the optimal evaluation order so that subsets are evaluated before dependent supersets.
3. Incorporates real-time circular dependency detection, rejecting any configuration loops.

Practical Example: Dynamic Classroom Grouping

\

## Imagine managing software in a computer lab (Classroom 3), where student workstations need specific software while the teacher machine requires distinct tools:

**Create Set**: Create set `SET-CLASSROOM-3`.

**Included Attributes**: Add the classroom location attribute `LOC-ROOM-03`.

**Excluded Attributes**: Add the teacher workstation identifier `ROLE-TEACHER`.

### Fields

* Fault Definitions
* *Configuration > Fault Definitions*
* Modern systems administration requires transitioning from reactive helpdesk calls to automated, proactive fleet health telemetry.
* A **Fault Definition** is a diagnostic script dispatched to client machines to test for silent system degradation, misconfigurations, or hardware warnings.
* *Fault notification in the alert center*
* **Name**: Descriptive check name (e.g., `Low Disk Space on /var`).
* **Description**: Explanation of the detected anomaly and suggested remediation steps.

### **Enabled**: Enables scheduled execution of the diagnostic script on clients.

**Language**: Interpreter language (Python or Bash).

1. **Code**: Diagnostic script code.
2. **Included and Excluded Attributes**: Target scope defining which machines run this check.
3. **User Profiles**: Support technicians or operators notified when this fault triggers.
4. Execution Mechanics and Alert Lifecycle
5. Fault execution follows a clean and robust pattern:

#### The client runs the fault code during its periodic synchronization.

If the check passes, the script **produces no output** and exits with code 0.

```python
import shutil

total, used, free = shutil.disk_usage('/var')
percent_used = (used / total) * 100

if percent_used > 90:
    free_mb = free // (1024 * 1024)
    print(
        f"Espacio critico en /var: {percent_used:.1f}% ocupado ({free_mb} MB libres). "
        "Accion: ejecute 'apt clean' o revise ficheros de registro en /var/log."
    )
```

\

## If an anomaly is detected, the script prints a descriptive error message to standard output.

The client sends this output to the server, which automatically creates an active Fault record in the database.

The alert counter in the web console increments in real time, alerting support staff before users experience downtime.

Practical Example: Critical Disk Space Detection

#### NOTE
The following Python script checks whether the `/var` partition has less than 15% free space remaining:

### Fields

* User Profiles
* *Configuration > User Profiles*
* In migasfree, it is important to distinguish between **computer end-users** (people logging into managed desktops) and **console administrative users** (technicians, packagers, administrators).
* User Profiles manage the accounts, credentials, and access roles of administrative personnel.
* **Secure Provisioning:** The root bootstrap account created during cluster initialization should only be used for setup. Each team member must have an individual named account for auditability.
* **Username**: Unique login identifier.
* **Email**: User email address for notifications and password recovery.
* **First Name**: User’s first name.
* **Last Name**: User’s last name.
* **Token**: Secure API authentication token generated automatically for REST API calls.
* **Enabled**: Indicates whether the account is active. Disabling an account revokes access immediately without deleting audit history.
* **Superuser**: Grants full, unrestricted administrative privileges across all modules.
* **Staff**: Authorizes login to the web administration console.

\

## **Groups**: Role-based permission groups assigned to the user (e.g., *Domain Admin*, *Packager*, *Reader*).

**Domains**: List of organizational domains over which the user has administrative authority.

**User Permissions**: Specific individual permission overrides.

**Domain**: Currently active domain preference selected in the session.

| **Scope**: Currently active scope preference selected in the session.                                           | Groups                                                                         |
|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| *Configuration > Groups*                                                                                        | **Groups** organize user permissions into role-based security profiles (RBAC). |
| Upon initializing the database, migasfree creates a set of standard pre-configured role groups:                 | Group                                                                          |
| Key Responsibilities and Permissions                                                                            | **Domain Admin**                                                               |
| Domain Administrator. Can manage computers, create deployments within their assigned domain, and review faults. | **Configurator**                                                               |
| Configuration Manager. Can create and edit projects, platforms, formulas, and singularities.                    | **Liberator**                                                                  |
| Release Manager. Manages release policies, deployment schedules, and software packages.                         | **Packager**                                                                   |
| Software Manager. Authorized to upload packages to software stores via CLI or CI/CD.                            | **Computer Checker**                                                           |

### Fields

* Support Technician. Audits synchronizations, inspects faults, and handles daily helpdesk incidents.
* **Device Installer**

### Hardware Operator. Manages printer devices, drivers, and peripheral assignments.

**Reader**

Read-only Auditor. Can query tables, dashboards, and inventories without modifying state.

\

## **Name**: Group or role title (e.g., `Domain Admin`, `Packager`).

**Permissions**: List of granular CRUD permissions (create, read, update, delete) across data models.

Role Composition and Custom Groups

### Fields

* A user can belong to multiple groups simultaneously, inheriting the combined union of all permissions.
* Furthermore, administrators can create custom groups at any time to match specific organizational workflows.
* Domains
* *Configuration > Domains*
* A **Domain** represents a major organizational or territorial division within an enterprise (e.g., Education, Healthcare, Police, City Council).
* **Name**: Domain name (e.g., `DOM-EDUCATION`, `DOM-HEALTHCARE`).

### **Comment**: Internal documentation or notes regarding the domain.

**Included Attributes**: Mandatory attributes required for a computer to belong to this domain.

1. **Excluded Attributes**: Attributes disqualifying a computer from this domain.
2. **Available Tags**: Catalog of tags that domain administrators are allowed to use within their domain.
3. **Domain Administrators**: Users authorized to manage computers and deployments within this domain.

#### NOTE
Mechanics and Delegated Authority

\

## Domain governance follows a strict segmentation model:

**Automatic Membership**: The server evaluates attribute rules during client syncs to dynamically place computers into their respective domains.

**Visual Isolation**: When a Domain Admin logs in, the console automatically filters all views, tables, and deployments to show only assets belonging to their assigned domain.

**Operational Boundaries**: *Domain Admin* users can create deployments and assign packages only to computers within their domain, preventing cross-departmental configuration conflicts.

### Fields

* **Coordinated Deployment Policies**: Coordinating global vs. domain-specific deployments ensures enterprise-wide baselines (e.g., corporate antivirus) coexist cleanly with department-specific applications.
* Scopes
* *Configuration > Scopes*
* A **Scope** is a personalized filter defined by an individual administrator to narrow down their working view to a specific subset of machines.
* Unlike domains (which are corporate security boundaries), scopes are personal productivity filters created by technicians for daily tasks (e.g., focusing on a single building or classroom).

### **Name**: Descriptive scope title (e.g., `Building A - 3rd Floor`, `Science Lab`).

**Domain**: Target organizational domain against which the scope applies.

* **User**: Owner user account linked to the scope.
* **Included Attributes**: Attribute criteria defining which computers appear in the scope.
* **Excluded Attributes**: Attributes excluding specific machines from the scope.

\

## Activation and Filter Scope

When an administrator activates a scope from their navigation toolbar selector:

* The console displays the **translucent top banner** reminding the operator of the active filter.
* All table listings, dashboard statistics, and search results automatically restrict to matching computers.
* Clicking the close icon on the banner instantly clears the scope and returns the console to the complete domain view.
* Summary
* In this chapter we explored the configuration and modeling foundation of migasfree:

**Platforms and Projects**: Define supported operating systems, packaging systems, and distribution versions.

# Devices

> > Any sufficiently advanced technology is indistinguishable from magic.

In any medium-to-large organization, managing peripherals and printers has historically been one of the most frustrating and time-consuming tasks for IT departments.

Although the data model and interface of migasfree were designed with generic device management in mind, in practice the vast majority of managed peripherals are **network and local printers**.

The traditional approach—installing drivers machine by machine, manually configuring IP addresses, resolving manufacturer driver dependencies, and repeatedly attending helpdesk calls for paper trays or duplex settings—is costly, error-prone, and unscalable.

True to its philosophy, migasfree resolves this challenge through **abstraction and declarative management**:

* **Centralized Inventory**: Provides an exact record of which physical printers exist in the organization, their serial numbers, IP addresses, models, and locations.
* **Declarative Assignment**: Printers are not manually installed per machine; they are mapped to attributes (departments, classrooms, subnets, buildings).
* **Unattended Deployment**: During synchronization (`migasfree-client`), the client automatically installs required driver packages and creates CUPS print queues.
* **End-User Self-Service**: Through the `migasfree-play` catalog, users can install available office or floor printers with a single click without administrative privileges.
* **Transparent Hardware Replacement**: If a printer fails and is replaced by a different model, an atomic device swap in the console automatically reconfigures all workstations upon their next sync.

Throughout this chapter we will examine each component of the Devices module:

* **Manufacturers**: Registry of commercial printer brands.
* **Models**: Catalog of hardware models, PPD drivers, and connection interfaces.
* **Features**: Functional printing profiles and capabilities (Duplex, Black & White, Color, Envelopes).
* **Devices**: Physical inventory of printers, network parameters, and queue mappings.
* **Device Replacement**: Atomic printer swap mechanism.
* **Connections**: Definition of communication protocols and interface parameters (USB, TCP/Raw, LPD, Serial, Parallel).
* **Device Types**: Conceptual classification of peripherals.
* **Logical Devices**: Global view and auditing of print queues.
* **Drivers**: Global catalog of PPD files and required driver software packages.

\

## Overview

To eliminate the nightmare of manual printer management, migasfree structures device governance into five sequential stages:

The workflow follows these five stages:

1. **Hardware Catalog Definition**: Register **Manufacturers** (e.g., *HP*, *Epson*, *Kyocera*) and functional **Features** (*B&W*, *Color*, *Envelopes*).
2. **Models and Drivers Definition**: Register the **Model** (*AL-M300*), specify its interfaces (*TCP*, *USB*), and map PPD drivers and required packages per feature.
3. **Physical Printer Registration (Device)**: Create the **Device** record (*Printer-Finance-01*), select its model and connection, and enter its IP or USB port.
4. **Logical Mapping to Attributes**: In the device form, create **Logical Devices** mapping specific features to organizational attributes (*DEP_FINANCE*).
5. **Automatic Client Provisioning**: During each sync, clients install driver packages and configure local CUPS queues automatically.

Below, we analyze each component in detail.

\

## Manufacturers

*Devices > Manufacturers*

A **Manufacturer** represents the commercial brand or vendor of the hardware (such as *HP*, *Epson*, *Brother*, *Canon*, *Kyocera*, *Lexmark*, or *Ricoh*).

It forms the top taxonomic tier to categorize the hardware catalog.

### Fields

* **Name**: Unique descriptive name of the manufacturer (e.g., `EPSON`, `HP`).

\

## Models

*Devices > Models*

A **Model** defines a specific commercial product manufactured by a vendor (e.g., `LaserJet Pro M404n`, `AL-M300`).

The model bridges physical hardware, supported connection interfaces, and operating system PPD drivers.

### Fields

The model detail view is structured into two blocks:

**General**:

* **Type**: Peripheral category (by default, `Printer`).
* **Manufacturer**: Manufacturer the model belongs to (e.g., `EPSON`).
* **Connections**: List of supported communication interfaces (e.g., `TCP`, `USB`).
* **Name**: Commercial model name or part number (e.g., `AL-M300`).

**Drivers**:

Allows associating one or more PPD drivers directly with the model for each feature and target operating system project:

* **Project**: Target OS distribution and project (e.g., `Debian-13`).
* **Feature**: Functional capability governed by this driver (e.g., `BN`, `DUPLEX`).
* **Name**: Absolute path to the **.ppd** file on GNU/Linux clients (e.g., `/usr/share/ppd/acme/Epson_AL_M300-ps-es.ppd`).
* **Packages to install**: Name of the software package providing the driver files (e.g., `acme-epson-al-m300`).

### PPD Files and Driver Preparation

A **PPD** (*PostScript Printer Description*) file describes printer capabilities, page sizes, resolutions, trays, and font support to the CUPS subsystem.

Such files can be obtained directly from the manufacturer or through specialized open-source repositories such as [OpenPrinting](https://www.openprinting.org/printers).

Procedure to create custom PPD files with default options pre-set:

1. **Obtain the Base PPD**: Download the original PPD file from the vendor driver or OpenPrinting database.
2. **Install Printer Locally on Test Machine**: Configure the printer locally in CUPS.
3. **Adjust Graphical Options**: Set default options (paper tray, duplex, economy mode) via the CUPS web interface (`http://localhost:631`).
4. **Extract Modified PPD**: Retrieve the generated PPD file from `/etc/cups/ppd/<queue_name>.ppd`.
5. **Package and Upload to Server**: Package the PPD files into a custom `.deb` or `.rpm` package and upload it to the migasfree server.

\

## Features

*Devices > Features*

A **Feature** (technically named *Capability* in the internal data model) defines a specific functional printing profile or operational mode.

Its primary purpose is simplifying user workflows: rather than requiring users to manually navigate driver dialogs to select trays or duplex modes, migasfree presents pre-configured queues tailored to specific tasks.

For example, a single physical multifunction printer can expose multiple dedicated features:

* **BN / DRAFT**: Standard black-and-white printing, economic toner consumption, single-sided.
* **COLOR**: High-resolution color printing on photo paper.
* **MULTIPURPOSE**: Printing routed specifically to the manual feed tray (envelopes, certificates, cardstock).

By decoupling features, migasfree allows publishing **multiple logical print queues** pointing to the same physical hardware.

### Fields

* **Name**: Feature title or code (e.g., `BN`, `COLOR`, `DUPLEX`, `MP`).

\

## Devices

*Devices > Devices*

A **Device** represents a concrete, individual physical unit installed in the organization (with its unique IP address, serial number, or USB port).

Every device is linked to a hardware model, a connection interface, and its specific connection parameters.

### Fields

The device form is organized into two blocks:

**General**:

* **Name**: Unique physical printer identifier (e.g., `Printer-Finance-01`, `Reception-Desk`).
* **Available for Attributes**: Target attributes and tags defining which users can see and install this printer in `migasfree-play`.
* **Model**: Associated hardware model (e.g., `AL-M300`).
* **Connection**: Chosen communication protocol (`TCP`, `USB`, etc.).
* **Connection Fields**: Dynamically generated input fields defined by the connection type (e.g., `IP` for TCP, `URI` for USB).

**Logical Devices**:

Allows defining logical print queues directly on the physical device form:

* **Feature**: Printing capability activated for this queue (e.g., `BN`, `DUPLEX`).
* **Alternative Feature Name**: Optional custom queue description shown to end users.
* **Attributes**: Target attributes specifying which computers automatically receive this queue.

#### TIP
The fastest way to register a device is filling in its name, model, connection parameters, and adding logical queues directly in the device form.

### Client Provisioning

During periodic synchronization (or when running `migasfree-client` on demand):

1. The server evaluates the computer’s attributes and collects all assigned logical print queues.
2. It resolves the required hardware model, connection parameters, and PPD driver paths.
3. The migasfree client processes this payload, automatically installs required driver packages, and configures CUPS queues.
4. If a computer no longer matches target attributes (for instance, if moved to another department), the client automatically removes obsolete queues.

\

## Replacement

*Devices > Device Replacement*

In peripheral lifecycle management, hardware failures and model upgrades are inevitable.

Imagine a busy network printer shared by 200 users fails and must be replaced by a different model from a different vendor.

With migasfree, administrators simply execute an atomic **Device Replacement** in the web console.

### Replacement Mechanics

1. The administrator registers the new physical printer in the catalog.
2. Navigates to **Device Replacement**, selects the old printer and the new destination printer.
3. Upon confirmation, migasfree automatically reassigns all logical print queues, connection mappings, and attribute rules to the new hardware.

During their next synchronization, client computers automatically install new driver packages, purge obsolete CUPS queues, and configure the new printer without user intervention.

\

## Connections

*Devices > Connections*

A **Connection** defines the communication protocol or physical interface used to reach the peripheral.

migasfree includes **five default connection types** out of the box:

* **USB**: Direct local USB connection. Requires the `URI` parameter (e.g., `usb://EPSON/AL-M300`).
* **LPT**: Traditional parallel port connection. Requires the device node path (e.g., `/dev/lp0`).
* **TCP**: Direct raw TCP socket network connection (default port 9100 / AppSocket). Requires the `IP` parameter.
* **LPD**: Line Printer Daemon network protocol. Requires `IP` and remote queue `NAME`.
* **SRL**: Serial port connection. Requires device path (`/dev/ttyS0`) and baud rate parameters.

### Fields

* **Name**: Connection code or title (e.g., `TCP`, `USB`, `LPD`).
* **Device Type**: Peripheral category the connection applies to.
* **Fields**: Comma-separated list of required connection parameters (e.g., `IP`, `URI`, `PORT`).

### JSON Data Schema

The fields list serves as a dynamic form template when editing physical devices.

Parameters entered by administrators are stored as structured JSON objects in the database.

```json
{
  "IP": "192.168.1.150",
  "PORT": "9100",
  "LOCATION": "Planta 1 - Secretaría",
  "NAME": "HP LaserJet en Secretaría Central"
}
```

\

## Types

*Devices > Device Types*

A **Device Type** classifies the broad functional category of peripherals (e.g., `Printer`, `Scanner`, `Card Reader`).

Although designed with an extensible data model, the built-in default type is `PRINTER`.

### Fields

* **Name**: Device type title (by default, `PRINTER`).

\

## Logical Devices

*Devices > Logical Devices*

In short, a **Logical Device** is the actual print queue created in CUPS on client workstations.

Although typically created directly from the Physical Device detail view, this menu provides a global administrative audit view of all print queues across the organization.

### Fields

* **Device**: Physical printer hosting the queue (e.g., `Printer-Finance-01`).
* **Feature**: Functional capability assigned to this queue (e.g., `BN`, `DUPLEX`).
* **Alternative Feature Name**: Custom descriptive name for end users.
* **Attributes**: Target attributes and tags determining which computers receive this queue.

\

## Drivers

*Devices > Drivers*

A **Driver** defines the PPD file path, target operating system project, and software package requirements for a model.

Like Logical Devices, Drivers are usually managed inside the Model detail form, but this section provides a centralized audit catalog to:

* Audit which OS projects have drivers configured for each model.
* Perform bulk updates of driver package assignments.
* Verify PPD filesystem paths across the organization.

### Fields

* **Name**: Absolute path to the PPD file on clients (e.g., `/usr/share/ppd/acme/Epson_AL_M300-ps-es.ppd`).
* **Model**: Associated hardware model.
* **Project**: Target operating system project.
* **Feature**: Governed printing capability.
* **Packages to Install**: Space-separated list of required driver software packages.

\

## Hands-on Practice

To consolidate all concepts covered in this chapter, we will perform a complete hands-on exercise configuring an Epson AL-M300 printer with three distinct features:

* **BN**: Standard black-and-white printing.
* **MP**: Multipurpose tray printing (envelopes/labels).
* **DUPLEX**: Mandatory double-sided printing.

### 1. Preparing the Corporate PPD Package

Download the `fun-with-migasfree-examples` project containing sample driver files.

```bash
sudo apt-get install unzip wget
wget https://github.com/migasfree/fun-with-migasfree-examples/archive/master.zip
unzip master.zip
cd fun-with-migasfree-examples-master/acme-epson-al-m300

# Packages required for building
sudo apt update
sudo apt install devscripts build-essential debhelper dh-make
```

In the book examples repository, open the `acme-epson-al-m300` directory containing the sample PPDs.

```bash
ls usr/share/ppd/acme
```

```text
Epson_AL_M300-ps-es.ppd
Epson_AL_M300-MP-ps-es.ppd
Epson_AL_M300-duplex-ps-es.ppd
```

Build the corporate package and upload it to the migasfree server:

```bash
/usr/bin/debuild --no-tgz-check -us -uc
sudo migasfree upload -f ../acme-epson-al-m300_1.0_all.deb
```

Next, under **Release > Deployments**, create a deployment making the package available:

* **Name**: `Printers`
* **Project**: Matching your client project (e.g., `FWM`)
* **Included Attributes**: `All Systems`
* **Origin**: `Internal`
* **Available Packages**: `acme-epson-al-m300`

### 2. Creating Manufacturer and Features

* **Devices > Manufacturers**: Add manufacturer `EPSON`.
* **Devices > Features**: Create features `BN`, `MP`, and `DUPLEX`.

### 3. Defining Model and Drivers

Under **Devices > Models**, create the model with the following parameters:

* **Type**: `PRINTER`
* **Manufacturer**: `EPSON`
* **Connections**: Select `USB` and `TCP`.
* **Name**: `AL-M300`

Click **Save and continue editing**, and in the **Drivers** block add three drivers:

* **Driver 1**:
  * *Project*: Matching project
  * *Feature*: `BN`
  * *Name*: `/usr/share/ppd/acme/Epson_AL_M300-ps-es.ppd`
  * *Packages to install*: `acme-epson-al-m300`
* **Driver 2**:
  * *Project*: Matching project
  * *Feature*: `MP`
  * *Name*: `/usr/share/ppd/acme/Epson_AL_M300-MP-ps-es.ppd`
  * *Packages to install*: `acme-epson-al-m300`
* **Driver 3**:
  * *Project*: Matching project
  * *Feature*: `DUPLEX`
  * *Name*: `/usr/share/ppd/acme/Epson_AL_M300-duplex-ps-es.ppd`
  * *Packages to install*: `acme-epson-al-m300`

### 4. Registering Physical Printers and Assigning Queues

With the catalog configured, register two physical printers:

**Network Printer (TCP)**:

* **General** Block:
  * **Name**: `Printer1`
  * **Available for Attributes**: `All Systems` (allows users to self-install via migasfree-play).
  * **Model**: `AL-M300`
  * **Connection**: `TCP`
  * **Connection Fields**: Enter IP address (e.g., `192.168.1.200`).
* **Logical Devices** Block: Add three logical devices mapping features `BN`, `MP`, and `DUPLEX`.

**Local Printer (USB)**:

* **General** Block:
  * **Name**: `Printer2`
  * **Available for Attributes**: `All Systems`
  * **Model**: `AL-M300`
  * **Connection**: `USB`
* **Logical Devices** Block: Add three logical devices mapping features `BN`, `MP`, and `DUPLEX`.

### 5. Provisioning and Result on Workstations

Now users can launch `migasfree-play`, browse available printers, and install them on demand.

When client machines synchronize (periodically or via `migasfree-client`):

1. The client automatically installs the `acme-epson-al-m300` driver support package.
2. Configures local CUPS print queues with the selected PPD options and connection URIs.
3. Printers appear ready to use in all desktop applications.
4. If the network printer’s IP address or hardware model changes in the future, updating the device in the console automatically propagates to all endpoints upon next sync.

\

## Summary

The **Devices** module transforms traditional, manual peripheral administration into an agile, automated, and auditable workflow:

In this way, peripheral hardware lifecycle management achieves the exact same rigor, reproducibility, and declarative elegance as software packaging.

With peripheral devices fully integrated into the organizational model, in the next chapter we will examine **Release Management**: deployments, schedules, and software catalogs.

# Release

> > No good thing is pleasant to possess, without friends to share it with.

Having modeled fleet classification, formulas, and attributes in previous chapters, we now reach the engine that distributes, updates, and governs software across workstations: the **Release** module.

Mass software distribution in organizations with thousands of computers poses critical operational challenges:

* **Network Congestion Risk**: Attempting to have thousands of workstations download hundreds of megabytes simultaneously can saturate local subnets and WAN links.
* **Big Bang Service Disruptions**: Rolling out a new software version across all machines at once exposes the entire organization to unforeseen bugs.
* **Repository Heterogeneity**: Coexistence of custom internal software with official third-party repositories.
* **User Autonomy vs. Central Governance**: Balancing centralized administrative control with self-service software installation for end users.

The **Release** module provides a unified, deterministic answer to all these challenges through **Deployments**, **Schedules**, **Software Stores**, and the **migasfree-play Application Catalog**.

Throughout this chapter we will examine its components in detail:

* Organizing packages using **Stores**, **Packages**, and **Package Sets**.
* The central delivery engine: **Deployments** (internal and external).
* Progressive, controlled rollout via **Schedules** and **Modular Arithmetic**.
* The graphical end-user self-service catalog: **Applications** and **Categories**.
* Exclusivity and coexistence rules through **Policies**.
* Best practices for the **Release Manager** role.
* A complete hands-on corporate software release case study.

\

## Overview

In migasfree, software delivery is not based on pushing blind scripts over SSH; it is founded upon the native package management system and dynamic, schedulable repositories.

The software lifecycle in the Release module follows these sequential stages:

1. **Ingestion and Indexing**: Software packages are uploaded to **Stores** and indexed by PMS services.
2. **Set Structuring**: Interdependent packages are grouped into logical **Package Sets**.
3. **Deployment Definition**: **Deployment** policies map packages to target attributes.
4. **Temporal Scheduling**: Using **Schedules** and **Delays**, rollouts are phased over days or weeks.
5. **Graphical Catalog Publication**: Self-service tools are published to **Applications** in `migasfree-play`.
6. **Client Resolution and Convergence**: During synchronization, clients configure sources, resolve dependencies, and converge to the target state.

### Standard Repositories vs. migasfree Repositories

In standard operating systems, package managers point to remote public repositories that can change or introduce breaking updates without organizational oversight.

To safeguard fleet stability, migasfree interposes a managed abstraction layer:

1. **Upstream Decoupling**: Endpoints never query public external repositories directly; all traffic is mediated by migasfree.
2. **Frozen Repositories**: Allows freezing upstream repositories to guarantee immutable testing baselines.
3. **Bandwidth Optimization**: The server caches packages locally, eliminating redundant external WAN downloads across thousands of machines.

During client synchronization (`migasfree sync`), the agent configures local package sources pointing directly to the server.

#### Repository Configuration Files on Workstations

| Package Manager / OS                   | Client Configuration File                      |
|----------------------------------------|------------------------------------------------|
| **APT** (Debian / Ubuntu)              | `/etc/apt/sources.list.d/migasfree.list`       |
| **DNF / YUM** (Fedora / RHEL / CentOS) | `/etc/yum.repos.d/migasfree.repo`              |
| **APK** (Alpine Linux)                 | `/etc/apk/repositories.d/migasfree.list`       |
| **ZYpp** (openSUSE / SLES)             | `/etc/zypp/repos.d/migasfree.repo`             |
| **WPT** (Windows Package Tool)         | Centralized local WPT repository configuration |
\

## Stores

*Release > Stores*

A **Store** is a designated folder on the server where software packages belonging to a project are organized.

Structurally, each store resides in the shared storage path `/public/<project>/<store>/`.

```text
/public/<slug-proyecto>/stores/<slug-almacen>/
```

This allows segregating packages by purpose (e.g., `corporate`, `third-party`, `drivers`, `testing`).

### Fields

* **Project**: Target operating system project the store belongs to.
* **Name**: Descriptive store name (e.g., `Corporate`, `Base`).

### Storage Lifecycle

* **Automatic Creation**: Created via the web console under **Release > Stores**.
* **CLI Creation**: Using the `migasfree upload` command creates the destination store automatically if it does not exist.
* **Safe Cascading Deletion**: Deleting a store cleans up database metadata while preserving files in shared storage.

\

## Packages

*Release > Packages*

A **Package** is a structured software archive (`.deb`, `.rpm`, `.pkg.tar.zst`, `.apk`, `.wpt`).

It can deliver applications, libraries, configuration files, scripts, or wallpaper assets.

Packages constitute the fundamental units of software governed by the server. They are categorized into two types:

* **Internal**: Packages uploaded directly to the migasfree server stores.
* **External**: Packages originating from official upstream remote repositories orchestrated by migasfree.

### Fields

* **Name**: Base package name without version or extension (e.g., `firefox-esr`, `acme-custom-config`).
* **Version**: String identifying package version and release revision (e.g., `128.0.1-1~deb12u1`).
* **Architecture**: Target binary architecture (`amd64`, `arm64`, `all`, `noarch`).
* **Project**: Operating system project the package belongs to.
* **Store**: Specific store where the binary file is located.

### Automatic Name Normalization

Upon uploading a package file, the server runs a normalization algorithm:

1. Detects file extension and verifies packaging format compatibility.
2. Extracts target CPU architecture from standard package suffixes.
3. Parses package name and version string following packaging standards.
4. Stores the binary in the target store and indexes its control metadata.

### Uploading from the Command Line

To upload individual packages to the server from a terminal without opening the web browser:

```bash
sudo migasfree upload --file <archivo-paquete>
```

The client uploads the file and triggers automatic PMS repository indexation.

### Difference between Stores and Repositories

It is critical to distinguish both concepts on the server:

* **Store**: The directory where uploaded package binaries are organized and stored.
* **Repository**: The signed package index and metadata structure generated by PMS services for client package managers.

### Detecting and Cleaning Orphan Packages

The alert center continuously monitors for packages in stores not assigned to any active deployment.

This alerts packagers to obsolete or unreleased packages occupying disk space.

\

## Package Sets

*Release > Package Sets*

A **Package Set** groups multiple packages from a store into a single logical entity.

Its purpose is simplifying the administration of interdependent software suites (such as LibreOffice language packs, printer drivers, or LAMP stacks).

### Fields

* **Name**: Set title (e.g., `Graphic Design Tools`, `Office Suite`).
* **Project**: Target project for member packages.
* **Store**: Specific store hosting member packages.
* **Description**: Detailed functional notes describing the package set.

### Bulk Upload from the Command Line

In addition to web console management, full directories of packages can be uploaded as a set using:

```bash
sudo migasfree upload --dir <directorio>
```

The command uploads files, creates the store if needed, and groups them into a package set in one step.

\

## Deployments

*Release > Deployments*

A [Deployment](annex05-glossary.md#term-Despliegue) is the central building block of software delivery in migasfree.

A deployment connects package sources (internal stores or external repositories) with target attributes and progressive rollout schedules.

### Fields

#### General Fields

* **Name**: Descriptive deployment title (e.g., `Base System Software`, `VLC Player`).
* **Enabled**: If unchecked, the deployment is suspended and ignored by client synchronizations.
* **Project**: Base operating system project evaluated by the deployment.
* **Domain**: Organizational domain the deployment is restricted to.
* **Origin**: Deployment source mode: **Internal (I)** for locally hosted packages, or **External (E)** for remote repositories.
* **Included Attributes**: Mandatory attributes required to receive this deployment (e.g., `SET-All Systems`, `DEP-FINANCE`).
* **Excluded Attributes**: Attributes disqualifying a computer from receiving this deployment.
* **Comment**: Technical changelog and change request rationale.
  ```text
  [alberto@2026-03-09] Añadido paquete corporativo-v2.1_amd64.deb
  [eduardo@2026-04-10] Desactivado temporalmente por incompatibilidad con driver X
  [alberto@2026-04-12] Reanudado despliegue tras corregir paquete v2.2
  ```
* **Schedule**: Progressive rollout schedule regulating staged delivery over time.
* **Start Date**: Date and time from which the deployment becomes active.
* **Auto Restart**: If checked, automatically restarts the schedule cycle when new packages are added.

#### The Five Package Action Fields

To precisely govern what happens on client endpoints, a deployment provides five distinct package action fields:

**Continuously evaluated during every synchronization:**

1. **Packages to Install**: Mandatory packages that must be installed and kept present on the system.
2. **Packages to Uninstall**: Prohibited packages that must be removed or purged from the system.

**Evaluated only upon computer tag changes:**

These three fields **do not execute during routine syncs**, but only when an administrator modifies computer tags:

1. **Pre-included Default Packages**: Preparatory dependencies installed prior to applying main packages.
2. **Included Default Packages**: Packages installed once when a tag is assigned, leaving users free to modify them later.
3. **Excluded Default Packages**: Packages uninstalled once when a tag is assigned.

#### Internal Origin Fields

When Origin is **Internal (I)**, packages are served directly from server stores:

* **Available Packages**: Individual packages selected from internal stores to include in the repository index.
* **Available Package Sets**: Complete package sets included in the repository index.

#### External Origin Fields

When Origin is **External (E)**, the deployment bridges to an official remote repository:

* **Base URL**: HTTP/HTTPS address of the remote repository.
* **Suite**: Distribution branch or codename (e.g., `bookworm`, `noble`, `40`).
* **Components**: Repository sections to enable (e.g., `main restricted universe multiverse`).
* **Options**: Extra APT/YUM line parameters (e.g., `[arch=amd64]`, `gpgcheck=1`).
* **Expiration**: Cache expiration time in minutes after which the server refreshes upstream metadata.
* **Frozen**: If checked, freezes the repository state locally, shielding the fleet from upstream changes.

#### Deployment Actions

The web console provides two powerful maintenance actions on deployments:

* **Regenerate Metadata**: Asynchronously forces PMS indexers to rebuild and re-sign repository indexes.
* **Copy Deployments Between Projects**: A migration wizard that duplicates a deployment to another project:
  1. Creates corresponding stores in the destination project.
  2. Copies package binaries in shared storage.
  3. Registers packages and sets linked to the new project.
  4. Clones the deployment and regenerates destination repository indexes.

\

### External Deployment Recipes

Below is a collection of tested production configurations for external deployments:

#### Ubuntu Noble (Base Frozen)

* **Name**: `UBUNTU-NOBLE-BASE`
* **Base URL**: `http://es.archive.ubuntu.com/ubuntu`
* **Suite**: `noble`
* **Components**: `main restricted universe multiverse`
* **Frozen**: Checked (True)
* **Options**: `[arch=amd64]`

#### Ubuntu Noble Security (Continuous Security Updates)

* **Name**: `UBUNTU-NOBLE-SECURITY`
* **Base URL**: `http://es.archive.ubuntu.com/ubuntu`
* **Suite**: `noble-security`
* **Components**: `main restricted universe multiverse`
* **Frozen**: Unchecked (False)
* **Expiration**: `1440` (server refreshes upstream metadata every 24 hours).
* **Options**: `[arch=amd64]`

#### Debian Bookworm (Official Base)

* **Name**: `DEBIAN-BOOKWORM-BASE`
* **Base URL**: `http://deb.debian.org/debian`
* **Suite**: `bookworm`
* **Components**: `main contrib non-free non-free-firmware`
* **Frozen**: Checked (True)
* **Options**: `[arch=amd64]`

#### Launchpad PPA Repository (Example)

* **Name**: `PPA-CUSTOM-SOFTWARE`
* **Base URL**:

  `https://ppa.launchpadcontent.net/author-name/ppa-name/ubuntu`
* **Suite**: `noble`
* **Components**: `main`
* **Frozen**: Checked (True)
* **Options**: `[arch=amd64]`

#### Fedora Linux (Base RPM)

* **Name**: `FEDORA-BASE`
* **Base URL**: `https://download.fedoraproject.org/pub/fedora/linux/releases/`
* **Suite**: `40`
* **Components**: `Everything/x86_64/os`
* **Frozen**: Checked (True)
* **Options**: `gpgcheck=1` `gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-40-x86_64`

#### Alpine Linux (APK)

* **Name**: `ALPINE-MAIN`
* **Base URL**: `https://dl-cdn.alpinelinux.org/alpine`
* **Suite**: `v3.20`
* **Components**: `main community`
* **Frozen**: Checked (True)

#### Federated Origin (Linking to Another migasfree Server)

In distributed multi-server architectures with central and regional servers:

* **Name**: `MIGASFREE-CENTRAL-REPO`
* **Base URL**: `http://central-server.domain.org/public/<project>/<store>/`
* **Suite**: `<central-deployment-name>`
* **Components**: `PKGS`
* **Frozen**: Checked (True)

\

## Schedules

*Release > Schedules*

Simultaneous software rollouts across thousands of endpoints risk network congestion and widespread disruption if an unpredicted defect arises.

A **Schedule** defines a phased rollout plan that delivers updates progressively over days or weeks.

### Fields

* **Name**: Schedule title (e.g., `SLOW`, `NORMAL`, `URGENT`).
* **Description**: Detailed functional notes explaining the rollout timeline.

### Delay Rules

A schedule is composed of one or more **Delay Rules** (*Schedule Delays*):

* **Delay**: Number of working days (excluding weekends) to wait before initiating this phase.
* **Duration**: Number of working days over which the rollout is evenly staged.
* **Attributes**: Required attributes to participate in this rollout phase (e.g., `PILOT-GROUP`, `All Systems`).

For example, inspect the built-in schedule `4 weeks (by MID)` in the web console:

* **Delay**: `0` (starts immediately on deployment start date).
* **Duration**: `20` (staged evenly over 20 working days, exactly 4 calendar weeks).
* **Attributes**: `All Systems`.

In this way, the server deterministically distributes 5% of the fleet each working day.

### Modular Arithmetic Staged Rollout Algorithm (MID)

To evenly and deterministically distribute computers across rollout days, migasfree uses **Modular Arithmetic based on Computer ID (MID)**:

The **modulo operation** computes the remainder of dividing the machine’s numeric ID (MID) by the total duration in days:

* Remainder **0**: Receives update on **Day 1**.
* Remainder **1**: Receives update on **Day 2**.
* Remainder **2**: Receives update on **Day 3**.
* Remainder **3**: Receives update on **Day 4**.
* Remainder **4**: Receives update on **Day 5**.

This algorithm provides distinct advantages:

1. **Uniform Load Balancing**: Request and download rates remain steady without network spikes.
2. **Absolute Determinism**: Requires no volatile runtime tracking; every computer calculates its assigned phase mathematically.
3. **Immediate Incident Mitigation**: If support reports a defect on Day 1, disabling the deployment instantly halts rollout for the remaining 95% of the fleet.

### Corporate Rollout Schedule Strategies

Enterprise IT departments typically maintain three standard schedule templates:

#### Typical Schedule Strategies and Templates

| Schedule Type         | Use Case                                                                          | Recommended Phases and Delays                                                                                                                                                                                              |
|-----------------------|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **SLOW**              | Major OS upgrades, core desktop suites, critical line-of-business applications.   | * Delay 0 (Duration 1): IT Support Team (`GRP-IT`)<br/>* Delay 5 (Duration 2): Pilot User Groups (`PILOT`)<br/>* Delay 10 (Duration 3): General Departments<br/>* Delay 15 (Duration 10): Entire Fleet (`SET-All Systems`) |
| **NORMAL**            | Routine application updates, minor utilities, routine maintenance patches.        | * Delay 0 (Duration 1): Pilot Group (`PILOT`)<br/>* Delay 3 (Duration 5): Entire Fleet (`SET-All Systems`)                                                                                                                 |
| **URGENT / ZERO-DAY** | Critical security patches addressing actively exploited zero-day vulnerabilities. | * Delay 0 (Duration 1): Rapid Validation Group<br/>* Delay 1 (Duration 2): Entire Fleet (`SET-All Systems`)                                                                                                                |

### Timeline Visualization and Lifecycle

Assigning a schedule to a deployment displays an interactive timeline widget in the web console showing current phase progress.

**Post-Rollout Consolidation**: Once a staged deployment finishes its duration and reaches 100% of machines:

1. Move consolidated packages into the permanent **Base Permanent Deployment**.
2. **Disable** (do not delete) the temporary staged deployment to maintain historical auditability.

### Case Study: Hardware Remediation via Attribute Sets and Schedules

Imagine a mixed fleet where a specific Wi-Fi chipset experiences connection drops under a kernel driver update.

After verifying a workaround configuration package in the lab:

1. **Exact Hardware Targeting**: The hardware formula identifies the Wi-Fi card PCI ID and generates attribute `HW_WIFI_RTL8821CE`.
2. **Staged Deployment**: A dedicated deployment targets `HW_WIFI_RTL8821CE` with a 3-day schedule.
3. **Controlled Rollout**: The server rolls out the fix exclusively to affected machines without touching unaffected hardware.

\

## Applications

*Release > Applications*

While deployments manage mandatory baseline system software, the **Applications** module powers the end-user self-service software store: `migasfree-play`.

Through `migasfree-play`, end users can browse, install, and uninstall authorized organizational software with a single click.

### Fields

* **Name**: Public commercial application name (e.g., `VLC Media Player`, `GIMP`, `Obsidian`).
* **Category**: Thematic catalog category (e.g., `Office`, `Design & Multimedia`).
* **Access Level**:
  * **User (U)**: End users can install or uninstall the software without administrative privileges.
  * **Administrator (A)**: Requires elevated administrator credentials to install.
* **Score**: Institutional rating or priority (displayed as 1 to 5 stars in the catalog).
* **Icon**: Representative application icon in SVG or PNG format.
* **Available for Attributes**: Target attributes required for the application to appear in a user’s catalog.
* **Description**: Rich text description detailing features and user guides.

### Search Optimization

The `migasfree-play` search engine indexes application names, descriptions, and keywords simultaneously.

A helpful practice is adding common alternative terms (e.g., adding “Photoshop” to GIMP’s description) to guide users migrating to open-source tools.

### Packages by Project

A single conceptual application (like “LibreOffice Suite”) may require different package names across distributions (e.g., `libreoffice-fresh` on Fedora vs. `libreoffice` on Debian).

Through **Packages by Project**, an application maps to its specific binary package names for each supported OS project.

\

## Application Categories

*Release > Application Categories*

An **Application Category** organizes applications into thematic sections in `migasfree-play`.

Standard categories include:

* **Office & Productivity**: Word processors, spreadsheets, email clients, PDF editors.
* **Education & Science**: Educational software, lab simulators, math tools.
* **Design & Multimedia**: Image editors, 3D modeling, audio/video players.
* **Development & Engineering**: IDEs, text editors, Git clients, virtualization tools.
* **System Utilities**: Compression utilities, backup tools, remote assistance.

### Fields

* **Name**: Category name (e.g., `Office`, `Multimedia`).

\

## Policies

*Release > Policies*

In advanced software management, not all deployment rules follow static inclusion criteria; some require mutual exclusivity and conditional precedence.

### Why use Policies instead of multiple Deployments?

Imagine configuring exam computer labs where student machines must strictly block USB storage devices, while teachers need unrestricted USB access in the same room.

Without policies, achieving this would require complex, fragile inverted attribute sets and complementary deployments.

1. Policy Fields
2. **Name**: Descriptive policy title (e.g., `Classroom USB Storage Policy`).
3. **Enabled**: Toggles active evaluation of the policy.
4. **Exclusive**: If checked, once an endpoint matches a priority group, the server stops evaluating subsequent groups and purges conflicting applications.

**Comment**: Administrative justification and purpose.

### **Included and Excluded Attributes**: Scope defining which machines evaluate this policy.

* Policy Groups
* Within a policy, one or more ordered **Policy Groups** are defined:
* **Priority**: Integer ranking evaluation order (lower numbers evaluated first).
* **Included and Excluded Attributes**: Membership criteria for this group.
* **Applications**: Collection of catalog applications assigned to this group.

### Algorithmic Evaluation Mechanics

During client synchronization:

* The server verifies the policy is **Enabled** and the client matches root attributes.
* Evaluates policy groups in ascending order of **Priority**.
* Upon finding the first matching group:

### Injects installation directives for all applications in that group.

During client synchronization:

1. The server verifies the policy is **Enabled** and the client matches root attributes.
2. Evaluates policy groups in ascending order of **Priority**.
3. Upon finding the first matching group:
   * Injects installation directives for all applications in that group.
   * If **Exclusive** mode is active, automatically instructs the client to uninstall all applications from all other groups in this policy.
   * Halts policy evaluation for that computer, guaranteeing mutually exclusive configuration.

### Practical Example: USB Storage Control in Classrooms

A classic requirement in educational centers is restricting USB flash drive access during exams:

1. Create the application `USB-LOCK` in the catalog.
2. Create an exclusive policy with the following parameters:
   * **Name**: `Classroom USB Storage Control`
   * **Exclusive**: Checked (True)
   * **Included Attributes**: `SET-All Systems`
   * **Group Priority 1** (Teachers): Attributes: `USR-teacher` | Applications:  *(none)*
   * **Group Priority 2** (Students and General Users): Attributes: `SET-All Systems` | Applications: `USB-LOCK`

**Evaluation Outcome**:

* **When a teacher logs in (\`\`USR-teacher\`\`)**: Priority 1 matches; no restrictions apply, and `USB-LOCK` is uninstalled if present.
* **When a student logs in**: Priority 1 does not match; Priority 2 evaluates and enforces `USB-LOCK` automatically.

\

## Hands-on Case Study

To consolidate all studied concepts, we will walk through a complete end-to-end workflow: deploying the knowledge management app [Obsidian](https://obsidian.md) (distributed as a standalone `.deb` package without an official APT repository) with staged rollout and self-service catalog publication.

### Step 1: Uploading the Package to the Store

Download the `.deb` package from official releases on GitHub ([obsidianmd/obsidian-releases](https://github.com/obsidianmd/obsidian-releases/releases)) and upload it to the server:

```bash
wget https://github.com/obsidianmd/obsidian-releases/releases/download/v1.13.7/obsidian_1.13.7_amd64.deb
sudo migasfree upload --file obsidian_1.13.7_amd64.deb
```

The upload wizard will prompt for credentials:

* **User**: Authorized packager username.
* **Password**: Packager password.
* **Project**: `FWM`
* **Store**: `others`

The command uploads the binary and registers package metadata in the database.

Notice an orphan package alert appears in the alert center awaiting deployment assignment.

### Step 2: Creating the Deployment with Staged Schedule

Under **Release > Deployments**, create a deployment to distribute Obsidian:

* **Name**: `Obsidian`
* **Project**: `FWM`
* **Origin**: `Internal`
* **Available Packages**: Select `obsidian`.
* **Schedule**: Select `4 weeks (by MID)`.

With this configuration, the server generates the signed repository index.

However, to perform an immediate test on our lab machine without waiting for its scheduled phase:

* **Included Attributes**: `CID-1`

Save the deployment and test installation on the client:

```bash
sudo migasfree sync
sudo migasfree install obsidian
sudo migasfree purge obsidian
```

The `migasfree sync` command updates repository sources in `/etc/apt/sources.list.d/migasfree.list`.

#### NOTE
Commands `migasfree install` and `migasfree purge` provide distribution-agnostic package management.

### Step 3: Publishing to the migasfree-play Graphical Catalog

In the web console under **Release > Applications**, add the application:

* **Name**: `Obsidian`
* **Category**: `Office`
* **Level**: `User` (installable without root privileges).
* **Score**: 4 stars.
* **Icon**: Upload an Obsidian logo image.
* **Available for Attributes**: `All Systems`
* **Description**:  *«Powerful knowledge base and Markdown note editor.»*
* **Projects**: Click *Add another project*:
  * **Project**: `FWM`
  * **Packages to Install**: `obsidian`

With this configuration, the application is published in the end-user store.

### Step 4: Verification on Client Workstations

Upon synchronizing the test machine (or any endpoint reaching its scheduled rollout day):

```bash
sudo migasfree sync
```

1. The client updates its repository sources in `/etc/apt/sources.list.d/migasfree.list`.
2. Repository indexes refresh transparently in the background.
3. The user opens `migasfree-play` and sees Obsidian available for one-click installation.

### Step 5: Post-Rollout Consolidation

After the four-week schedule completes and all endpoints have updated, consolidate the deployment into the permanent base repository and disable the temporary deployment.

\

## Best Practices

To ensure orderly software governance in enterprise fleets:

1. **Naming Traceability**: Include change request ticket IDs in deployment names (e.g., `DEP-OBSIDIAN-REQ-4821`).
2. **Comment Log as a Living Journal**: Record reasons, dates, and author information in deployment comments.
3. **Pre-validation in Lab and Pilot Groups**: Never release software globally without prior pilot group testing.
4. **Package Catalog Hygiene**: Periodically review orphan packages and purge obsolete versions.
5. **Consolidation and Decommissioning**: Do not accumulate dozens of temporary deployments; consolidate packages into base deployments once rolled out.

\

## Summary

In this chapter we analyzed the software delivery engine of migasfree in depth:

* **Stores, Packages, and Sets**: Structured, secure software storage on the server.
* **Deployments (Internal and External)**: Declarative software delivery and external repository orchestration.
* **External Deployment Recipes**: Practical templates for Ubuntu, Debian, Fedora, Alpine, and federated servers.
* **Schedules and Modular Arithmetic**: Eliminating rollout risks through deterministic, staged fleet delivery.
* **Applications and Categories**: An intuitive self-service software store via `migasfree-play`.
* **Policies and Exclusivity**: Solving complex conditional software delivery and mutual exclusivity scenarios.
* **Release Best Practices**: Ensuring traceability, hygiene, and stability across enterprise fleets.

All this delivery machinery assumes, however, that the operating system has already been installed on the machine.

So much software packaging and modular mathematics calls for a well-deserved break!

Take a breather, and let us continue to Master Images!

# Master Images

> > First, solve the problem. Then, write the code.

We have now covered the declarative modeling of migasfree: first the organizational structure with Projects, Formulas, and Attributes (Chapter 12); then hardware and peripheral fleet governance with Devices (Chapter 13); and finally, the software delivery and lifecycle engine with Deployments, Schedules, and Policies (Chapter 14).

From the **Master Images** (*Migasfree Golden Images* or **MGI**) module, we have already experienced a practical introduction: in Chapter 6 we used the `fwm` template to clone a workstation using MCS. Now we will study in depth how this base image generation engine operates.

In classical systems administration, that base was manufactured manually:

* A technician manually installed an operating system on a reference computer.
* Configured applications, removed temporary users, and ran cleanup scripts.
* Captured the disk using static sector-level cloning tools (Clonezilla, Ghost, Partimage).

The result suffered from severe reproducibility problems: images degraded over time, nobody remembered the exact commands executed on the reference machine, and any modification forced repeating the entire process from scratch.

In the first decade of the 21st century, **Infrastructure as Code** (*IaC*) established that provisioning servers, networks, and storage can be described as versionable, reproducible, and auditable software rather than configured by hand. In that same spirit, migasfree applies this philosophy to the **base operating system**, defining images as [IaC](https://en.wikipedia.org/wiki/Infrastructure_as_code) code: declarative, automated, and reproducible:

* Images are defined via structured templates, Dockerfile recipes, YAML partition schemes, and Jinja2 provisioning scripts.
* Compilation runs unattended on the server inside lightweight containers or virtual machines.
* The result is optimized master images ready for high-speed deployment via MCS, complete with driver support and post-clone convergence.

Throughout this chapter we will model the four levels of MGI: **Configurations**, **Flavours**, **Releases**, and **Builds**.

#### NOTE
**The foundation is already set**: In Chapter 6 (Mass Provisioning) we learned how MCS streams and installs these images on workstations. Here we focus on the server-side engine that builds and publishes them.

Before proceeding, a reminder: MGI **Releases** represent true versioned baseline snapshots.

\

## Overview

The **Master Images** module allows designing and building operating system images completely from code and web console definitions.

The workflow combines the four levels you already know from Chapter 6, organized into two synchronized phases:

* **Compilation (CI)**: The administrator defines the base configuration and flavours, launching containerized or VM builds in Docker Swarm.
* **Publication (CD)**: The compiled image is published to the shared storage repository (`/pool/mgi/`) and made available to MCS for network or local cloning.

\

Before examining each form in detail, let us remember how each piece fits into the pipeline.

## Configurations

*Master Images > Configurations*

A **Configuration** represents the master template that defines the technical foundation of the operating system.

Each configuration is linked to a single migasfree project and target CPU architecture.

### Form Fields

The configuration form models the complete system recipe:

* **Project**: The migasfree project the image belongs to (e.g., `FWM`, `AZL-22`).
* **Template Identifier**: Internal template key (e.g., `fwm`, `debian-13`).
* **Build Engine**: Build engine used to generate the image:
  - **Docker** (Linux): Builds the filesystem root (*rootfs*) inside Docker containers using `debootstrap`/`dnf` and container layers.
  - **QEMU Preseed / Kickstart** (Linux): Runs a headless QEMU virtual machine to perform automated unattended OS installations.
  - **QEMU Unattended** (Windows): Installs Windows in a virtual machine using unattended XML answer files (`Autounattend.xml`).
* **Image Format**: Output format of the compiled image:
  - **RAW** (`.raw`): Raw block-level partition image, standard for high-speed MCS streaming.
  - **WIM** (`.wim`): File-based archive format standard for Windows imaging.
  - **SquashFS** (`.squashfs`): Highly compressed read-only filesystem format.
* **Base Operating System**: Upstream reference distribution (e.g., `Debian 13 (Trixie)`).
* **Partition Scheme**: YAML file (`partition.yml`) defining the disk layout (EFI, root, swap, home) and filesystem types (ext4, btrfs, ntfs).
* **Provisioning Script**: Post-installation shell script executed upon target deployment:
  1. **MCS Variable Declarations**: Declares user-customizable deployment parameters in script headers.
  2. **Execution and Rendering**: After writing disk blocks, MCS renders Jinja2 template variables and executes the script before first boot.
* **Dockerfile**: Jinja2 template defining the step-by-step image recipe.

  Overview of the phases comprising a typical MGI build recipe:
  1. **Base Structure and Dependencies**: Bootstraps the minimal OS filesystem and required packages.
  2. **Repository Configuration and migasfree Client**: Downloads and configures the client to connect to the server.
  3. **Storage and Boot (Initramfs / GRUB)**: Configures kernel modules, initramfs hooks, and bootloader configurations.
  4. **Registration, Synchronization, and Tag Injection**: Mocks hardware UUIDs, registers the build instance with the server, and runs `migasfree sync` to install assigned software.
  5. **Localization, Network, and Users**: Configures system locales, timezone (`{{ timezone }}`), keymaps, networkd, and default admin accounts.
  6. **Metadata and Cleanup**: Injects the build audit file `/etc/migasfree-golden-image.json`, cleans package caches, and unlinks the temporary build client.

\

## Flavours

*Master Images > Flavours*

A **Flavour** defines a specific functional variant built upon a master configuration.

In an enterprise, it is common to require multiple variants of the same OS: one for general office desktops, another for classrooms, another for engineering workstations, and another for branch servers.

Instead of duplicating full configurations, this model provides decisive advantages:

* **Centralized Maintenance**: Core engineering (partitioning, GRUB, repositories, base recipes) is defined once in the configuration; improvements are automatically inherited by all flavours, following the [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principle.
* **Declarative Customization**: Each flavour only specifies its identity variables, default credentials, localization settings, and **migasfree tags** (`{{ tags }}`).
* **Server Convergence**: Thanks to injected tags, during build time the client executes `migasfree sync` and installs the exact software governed for that profile.
* **Fast Layered Builds**: Sharing the same base image minimizes build times and optimizes storage.

### Fields

* **Configuration**: Master configuration the flavour is based upon.
* **Flavour Name**: Flavour identifier (e.g., `workstation`, `server`, `lab-cad`).
* **System Hostname**: Default network hostname assigned to provisioned machines (e.g., `PC-WORKSTATION`).
* **Enabled**: Toggles whether the flavour is active for builds and MCS deployments.
* **Description**: Brief functional summary of the flavour.
* **Default User**: Username for the initial local administrative account.
* **Default Password**: Default password assigned to the initial account.
* **System Timezone**: Timezone tzdata identifier (e.g., `Europe/Madrid`).
* **Associated Tags**: migasfree server tags assigned to machines cloned with this flavour.
* **Keyboard Layout (Keymap)**: Console and X11 keymap code (e.g., `es`, `us`).
* **Keyboard Model**: Hardware keyboard model (e.g., `pc105`).
* **Character Map (Charmap)**: Console character encoding (e.g., `UTF-8`).
* **Codeset**: Font codeset for Linux virtual consoles.

### Injecting migasfree Tags into the Base System

The integration between MGI and the migasfree server achieves its maximum synergy through tags:

1. When designing a flavour, the administrator assigns server tags (such as `FLV-WORKSTATION` or `DEP-FINANCE`).
2. During image compilation, the MGI engine writes these tags directly into `/etc/migasfree-tags` inside the Golden Image.
3. When cloned endpoints boot for the first time, `migasfree-client` reads these tags and submits them to the server.
4. The server matches assigned deployments and delivers all corporate software automatically.

Thus, flavours act as the natural bridge between initial bare-metal provisioning and ongoing fleet management.

\

## Releases

*Master Images > Releases*

A **Release** represents a frozen, versioned snapshot of a master configuration.

It allows maintaining rigorous version control over Golden Images (e.g., Release `1.0`, Release `2.0`).

### Form Fields

* **Configuration**: Master configuration whose state is snapshot.
* **Version**: Formal version string (e.g., `1.0`, `2024.1`).
* **Release Notes**: Summary describing the purpose and updates included in the release.

### Consolidating Updates

While production machines evolve daily via dynamic client synchronizations, new machines cloned months later would require extensive updates if provisioned from an outdated image.

Periodically creating a new MGI release (e.g., Release 1.1) consolidates all updates into the master image, ensuring fast bare-metal provisioning.

### Launching Builds

From the release detail view, the builds section allows triggering automated builds with a single click.

\

## Builds

*Master Images > Builds*

A **Build** is the **actual execution of an image generation task** in the cluster.

### Build Lifecycle

Generating an operating system image is an asynchronous workflow executed in Docker Swarm:

1. **Queued**: The administrator requests a build; the task enters the Celery queue.
2. **Running**: A worker container picks up the task, downloads base packages, and compiles the image.
3. **Completed**: The build finishes successfully; the compressed `.mgi` file is saved to `/pool/mgi/`.
4. **Failed**: If an error occurs during package download or recipe execution, the build fails and logs are saved for diagnosis.

Each build record provides full execution logs and artifact details.

### Publishing for Deployment

For quality control and safety, **a newly completed build is not visible in MCS by default**.

This allows administrators to test and validate images in test environments before production release:

1. **Prior Validation**: Technicians can download and test the image on lab machines.
2. **Formal Promotion**: Once verified, the administrator clicks the **Promote** button on the build record.
   ```text
   http://<FQDN_SERVIDOR>/pool/mgi/
   ```
3. **Visibility in MCS (Promoted Settings)**: Only promoted builds appear in the MCS deployment menu on client machines.

Operational details of MCS deployment—network streaming, local USB cloning, and user data preservation—are explored in [Chapter 18 (MCS)](chapter18.md#mcs).

\

## Summary

In this chapter we explored Golden Image engineering with the Master Images module:

* **Image-as-Code Approach**: Replaces manual capture with reproducible, version-controlled recipes.
* **Configurations**: The architectural blueprint (project, template, partition schemes, Dockerfile/Jinja2 recipes).
* **Flavours**: Functional variants on a shared base that inject tags to trigger automatic post-clone software convergence.
* **Releases and Builds**: Ensure rigorous versioning, asynchronous builds in Docker Swarm, and controlled promotion.

With the base operating system declared and built, we conclude Block B (Console and Modeling). Next, we enter Block C: The Client Environment.

# C. Client

This final block of Part III closes the loop: after defining server infrastructure and modeling the organization through the web console, we now focus on the software components running directly on managed endpoints.

Across four chapters we will explore the pieces that complete the migasfree ecosystem:

* [Chapter 16 (Client Environment)](chapter16.md#entorno-cliente): the Client Triad (`migasfree-client`, `migasfree-agent`, and `migasfree-play`) in GNU/Linux environments, its synchronization lifecycle, and operational mechanisms.
* [Chapter 17 (Windows Environment)](chapter17.md#entorno-windows): seamless integration of Microsoft Windows endpoints into the platform using Windows Package Tool (WPT) and the hardware inventory emulator.
* [Chapter 18 (MCS)](chapter18.md#mcs): bare-metal mass provisioning with Migasfree Cloning System, network and local cloning, and home directory preservation.
* [Chapter 19 (Data)](chapter19.md#datos): fleet inspection, hardware/software telemetry, relational querying, and data consumption via the REST API and the Model Context Protocol (MCP) server for AI assistants.

Upon completing this block, you will possess the complete picture of migasfree: from physical server infrastructure to daily endpoint management.

# Client Environment

> Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.

In previous chapters we thoroughly explored server infrastructure: microservices orchestration, the administration web console, policy modeling, and release store management. However, all that centralized machinery would lack purpose without the tools operating on the final destination of configuration: **managed computers**.

The client environment is where the theory of SCM transforms into operational reality. Far from being a passive recipient of commands, each computer managed by migasfree acts as an autonomous, intelligent agent capable of inspecting its own hardware, negotiating secure channels, evaluating declarative directives, executing atomic transactions with the local package manager, and offering continuous support.

In this chapter we will analyze the three pillars comprising the client ecosystem: the convergence engine [migasfree-client](https://github.com/migasfree/migasfree-client), the secure remote access agent [migasfree-agent](https://github.com/migasfree/migasfree-agent), and the self-service catalog [migasfree-play](https://github.com/migasfree/migasfree-play).

## The Triad

On computers managed by migasfree, up to three specialized components coexist with clearly differentiated yet closely coordinated roles (although on headless servers the visual layer of `migasfree-play` is omitted):

1. **migasfree-client (Synchronization and Convergence Engine)**: Executes periodically via system timers or at user login. It is the universal and essential component on every computer (workstation or server): it discovers hardware, queries assigned directives on the server, computes state differences, and applies required modifications using the operating system’s native package manager (APT, DNF, Pacman, APK, or WPT).
2. **migasfree-agent (Support Tunnel and Remote Access)**: Maintains a continuous, secure link with the server via WebSockets and mTLS. It facilitates immediate remote access (SSH, VNC, RDP) and launches synchronizations from the web console without open firewall ports or VPN tunnels.
3. **migasfree-play (Visual Self-Service Catalog)**: The desktop application accessible to end users in graphical environments (X11, Wayland, or Windows). It provides a visual catalog of authorized applications published for the machine based on its attributes, allowing users to install or uninstall software with a single click and without administrative privileges (`sudo`). On headless servers, this component is omitted.

This separation of concerns ensures maximum flexibility and security: user workstations enjoy an intuitive graphical experience without compromising local privileges, while infrastructure servers are managed in a lightweight, unattended manner.

## migasfree-client

[migasfree-client](https://github.com/migasfree/migasfree-client) is the operational heart of any machine managed by the platform. Implemented in Python, it runs natively on GNU/Linux and Microsoft Windows.

### CLI Anatomy and Subcommands

Although the client typically operates unattended, it provides a comprehensive set of subcommands for interactive management, local diagnostics, and administrative workflows:

```bash
# Consultar la ayuda general y los subcomandos disponibles
migasfree --help

# Sincronización estándar con el servidor
sudo migasfree sync

# Sincronización en modo depuración (muestra trazas detalladas)
sudo migasfree --debug sync

# Forzar sincronización de paquetes ignorando el ajuste Auto_Update_Packages
sudo migasfree sync --force-upgrade

# Sincronizar selectivamente un subsistema concreto
sudo migasfree sync --hardware
sudo migasfree sync --devices

# Consultar información del equipo registrada en el servidor (o en formato JSON)
migasfree info
migasfree info -j

# Consultar atributos asignados y el identificador CID del equipo
migasfree attributes -j
migasfree attributes --cid

# Consultar o asignar etiquetas al equipo desde la línea de órdenes
migasfree tags --get
sudo migasfree tags --set aula-01 primaria

# Mostrar la etiqueta identificativa del equipo en pantalla (soporte helpdesk)
migasfree label

# Buscar paquetes disponibles en los almacenes asignados
migasfree search <patrón>

# Instalar o desinstalar paquetes abstrayéndose del PMS local
sudo migasfree install <paquete>
sudo migasfree purge <paquete>

# Consultar o modificar la configuración local (/etc/migasfree.conf)
migasfree conf --json

# Importar manualmente certificados mTLS empaquetados
sudo migasfree import-mtls /ruta/certificado.tar

# Subir un paquete al almacén del servidor (desde puestos de empaquetado)
migasfree upload -f mi-paquete_1.0_all.deb -j Proyecto-Base -s almacén
```

### The Convergence Lifecycle Step by Step

Each time a synchronization executes (via `migasfree sync` or automated triggers), the client executes a deterministic six-phase cycle:

1. **Phase 1 — mTLS Negotiation, Availability, and Pre-Hooks**: The client establishes an encrypted TLS session, verifies server availability, validates its mTLS certificate, and executes scripts in `/etc/migasfree-client/pre-sync.d/`.
2. **Phase 2 — Attribute and Fault Evaluation and Reporting**: The client executes active formulas, generates identifying attributes, runs fault diagnostic checks, and submits collected metrics to the server.
3. **Phase 3 — Software Convergence with the PMS**: Based on received directives, the client configures repository sources, downloads required packages, and performs atomic install/purge transactions with the native package manager.
4. **Phase 4 — Hardware Introspection (On Demand)**: If the server requests hardware telemetry, the client scans DMI, PCI, USB, and memory devices and reports the structured inventory.
5. **Phase 5 — Logical Device Synchronization (Printers)**: Evaluates assigned logical devices, installs missing PPD drivers, and configures local CUPS print queues.
6. **Phase 6 — Traits, Reactive Events, and Post-Hooks Telemetry**: Updates the local traits state file (`/var/migasfree-client/traits.json`), triggers reactive event handlers (`events.d/`), and executes post-sync scripts (`post-sync.d/`).

### Traits and Extension Points

The **traits** represent the runtime snapshot of all attributes, tags, and deployments assigned to the machine by the server.

During Phase 2, the client only knows its raw attributes. In Phase 6, after server resolution, it receives the complete list of assigned traits.

```bash
# Query all consolidated traits of the computer
sudo migasfree traits

# Filter by prefix (e.g. USR)
sudo migasfree traits USR

# Get the exact value of a prefix (e.g. USR)
sudo migasfree --quiet traits USR value
```

To enable local customization without breaking the declarative model, the client provides two extension mechanisms:

* **Lifecycle Hooks (\`\`pre-sync.d/\`\` and \`\`post-sync.d/\`\`)**: Scripts executed before Phase 1 and after Phase 6, receiving context variables such as exit status and server FQDN.
* **Reactive Event Handlers (\`\`events.d/<prefix>/\`\`)**: Specialized scripts executed when a specific attribute or tag matching the directory prefix is assigned or removed.

#### NOTE
The detailed structure of hook directories, environment variables, and return codes is documented in Annex 4 (CLI Cheat Sheet).

### Key Files and Paths in the System

On GNU/Linux systems, client files follow standard FHS conventions:

#### NOTE
The complete table of data paths and logs on both GNU/Linux and Windows is detailed in Annex 4.

### Scheduled Execution

On servers or headless machines (where `migasfree-play` does not run), synchronizations are triggered automatically by systemd timers (`migasfree-client.timer`) or cron jobs.

## migasfree-agent

Traditionally, remote technical assistance has depended on port forwarding, dedicated VPNs, or third-party proprietary software. [migasfree-agent](https://github.com/migasfree/migasfree-agent) replaces all these architectures with a lightweight, secure **reverse tunnel** based on WebSockets and mTLS.

### Reverse Tunnel Architecture

Instead of listening for incoming connections, `migasfree-agent` initiates an outbound WebSocket connection to the server on port 443:

When a technician requests a remote session from the web console:

1. The server notifies the agent across the existing tunnel.
2. The agent establishes a multiplexed sub-tunnel for the requested protocol (SSH, VNC, RDP).
3. Traffic flows encrypted end-to-end without the endpoint exposing open inbound listening ports.

### Security and Command Whitelisting

To protect endpoint integrity and eliminate attack vectors:

* **Authenticated Tunnels**: Every connection requires mutual cryptographic verification (mTLS) with dedicated ephemeral tokens.
* **Remote Execution Whitelist**: In addition to interactive tunnels, the agent only executes pre-authorized administrative commands explicitly defined in local configuration.

### Service Management

The agent runs as a continuous system service managed by systemd:

```bash
# Consultar el estado del agente de acceso remoto
systemctl status migasfree-agent

# Inspeccionar los registros en tiempo real
journalctl -u migasfree-agent -f

# Reiniciar el agente tras cambios de red
sudo systemctl restart migasfree-agent
```

## migasfree-play

[migasfree-play](https://github.com/migasfree/migasfree-play) brings the power of centralized management to the desktop, empowering end users with self-service autonomy.

### Login Synchronization

The primary task of `migasfree-play` upon user login is triggering an asynchronous background synchronization to guarantee that user-level policies and printers are configured immediately.

### Application Modules

The `migasfree-play` user interface is organized into five functional modules:

1. **Application Catalog**: Allows browsing, installing, and uninstalling authorized applications with a single click.
2. **Device and Printer Catalog**: Allows browsing and installing available network and local printers.
3. **Tag Management**: Displays assigned tags and allows toggling self-service user tags.
4. **System Information**: Shows a comprehensive hardware, network, and operational summary of the machine.
5. **Trace Console and Logs**: Provides a real-time log viewer for troubleshooting.

## Troubleshooting and Diagnostics

Below is a summary of recommended diagnostic procedures for client tools:

#### Client Tools Incident Resolution

| Symptom or Error                     | Probable Cause                                                                         | Corrective Action                                                                          |
|--------------------------------------|----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Client mTLS Verification Failure     | Local certificate expired, corrupted, or revoked on server.                            | Remove `/var/migasfree-client/mtls/` and run `sudo migasfree sync` to re-enroll.           |
| Package Manager Lock Error           | Another package transaction was interrupted (e.g., stale `/var/lib/dpkg/lock`).        | Run `sudo dpkg --configure -a` or clear package locks before re-syncing.                   |
| `migasfree-agent` Disconnected       | DNS resolution failure or firewall blocking outbound HTTPS/WSS port 443.               | Verify connectivity using `curl -v https://<SERVER_FQDN>/tunnels/` and check logs.         |
| `migasfree-play` Shows Empty Catalog | No deployments assigned with user access level (**U**) for current machine attributes. | Verify deployment attribute targeting and application publication settings in web console. |

## Summary

Ultimately, client tools bring declarative policies to life on managed machines:

* **migasfree-client**: Operates in the background to ensure the machine converges deterministically to its Desired State.
* **migasfree-agent**: Enables real-time, secure remote assistance without VPNs or open inbound ports.
* **migasfree-play**: Empowers end users with a rich visual self-service software and printer store.

This [triad](annex05-glossary.md#term-Triada) provides a solid, uniform foundation to govern diverse desktop and server fleets.

Let us continue to Windows environments—but first, how about a quick coffee?

# Windows Environment

> Simplicity is about subtracting the obvious and adding the meaningful.

In modern systems administration, heterogeneity is not an exception: it is the norm. Even in organizations with an explicit commitment to Free Software and GNU/Linux desktop environments, it is common to find specialized Windows workstations for specific corporate software, computer-aided design (CAD), legacy business management tools, or laboratory instrumentation.

Attempting to govern a Windows environment under declarative SCM principles represents a formidable challenge. Windows was historically conceived as an operating system oriented toward individual interactive use rather than mass declarative automation. The absence of a native unified package manager, the proliferation of heterogeneous installers (MSI, InnoSetup, NSIS), and differences in hardware telemetry mechanisms have traditionally forced IT teams to maintain parallel, disconnected management silos.

Despite these challenges, migasfree does not compromise on integrating Microsoft Windows as a first-class citizen in its data model. In this chapter we will examine how to approach Windows workstation management with realism: the bridge tools developed (such as `WPT` or the `lshw` emulator), how software is structured, and the practical engineering compromises required to maintain control without losing your patience.

#### NOTE
This chapter builds upon the concepts explained in [Chapter 16 (Client Environment)](chapter16.md#entorno-cliente). To avoid redundancy, we focus exclusively on adaptations, tools, and specific characteristics of the Windows ecosystem.

## The Challenge

Managing Windows workstations poses substantial architectural challenges that differ radically from the UNIX experience:

1. **Historical Absence of a Unified System Package Manager**: While in Linux the operating system and applications share a single dependency graph governed by APT, DNF, or Pacman, in Windows each vendor ships its own executable installer (MSI, InnoSetup, InstallShield, NSIS, or custom binaries). Although tools like Winget or Chocolatey have emerged, neither was originally designed as a centralized corporate convergence engine operating under an attribute-based model with frozen version control and integrated auditability.
2. **Dependency Isolation and Conflicts**: Windows applications frequently bundle their own dynamic link libraries (DLLs) or require specific runtimes (such as exact Python interpreter versions or .NET Frameworks). Arbitrarily modifying global system variables like `%PATH%` can trigger cascading conflicts in pre-existing software.
3. **Divergence in Physical Hardware Inventory**: In GNU/Linux, hardware introspection relies on virtual filesystems (`/proc`, `/sys`) and standardized utilities such as `lshw`, `lspci`, and `lsusb`. In Windows, physical introspection is performed via Windows Management Instrumentation (WMI) and Common Information Model (CIM) queries.

To bridge this divide without forcing administrators to maintain two disconnected platforms, the migasfree project developed two foundational components: [windows-package-tool](https://github.com/migasfree/windows-package-tool) (WPT) and [lshw-windows-emulator](https://github.com/migasfree/lshw-windows-emulator).

## Hardware

Hardware inventory provides administrators with a comprehensive, centralized record of all physical components across the fleet (CPUs, RAM, storage, network interfaces, and peripherals). If the server received this data in fragmented, OS-dependent schemas, maintaining a consistent and auditable asset database would be impossible.

The [lshw-windows-emulator](https://github.com/migasfree/lshw-windows-emulator) package solves this problem at its root: it is a Python-based emulator that queries the Windows WMI interface to gather comprehensive telemetry on:

* **Motherboard and BIOS**: Manufacturer, model, serial number, and machine UUID.
* **Processor (CPU)**: Architecture (x86_64, ARM), core count, clock frequency, and instruction capabilities.
* **Physical Memory (RAM)**: Total capacity, populated slots, technology type, and speed.
* **Storage**: Local disks, unique drive serials, interface buses (NVMe, SATA), and partition schemes.
* **Network Adapters**: Physical interfaces, MAC addresses, and link status.
* **Graphics Controllers**: Integrated or discrete GPU, vendor, and video memory.

```powershell
# Invocación directa del emulador en una terminal de Windows
lshw -json
```

The emulator transforms WMI class structures (such as `Win32_Processor`, `Win32_BaseBoard`, `Win32_DiskDrive`) into an XML schema matching Linux `lshw -xml` output.

## WPT

[windows-package-tool](https://github.com/migasfree/windows-package-tool) (WPT) is the declarative, lightweight package manager developed specifically to bring Linux-like package management rigor to Microsoft Windows.

### Isolated Virtual Environment Strategy

One of the most innovative design principles of WPT is its **Isolated Virtual Environment Strategy**:

1. **Isolation with venv**: When installing any package (for example, `migasfree-client`), WPT creates an independent Python virtual environment (venv) inside `%PROGRAMDATA%\wpt\apps\<app_name>\`.
2. **Clean Registration in App Paths**: Instead of polluting the global `%PATH%` system variable, WPT registers application launchers cleanly in the Windows Registry under `HKLM\Software\Microsoft\Windows\CurrentVersion\App Paths`.

### WPT Installation and Suite Provisioning

Deploying migasfree on Windows follows a structured bootstrap workflow:

1. **Initial WPT Bootstrap**: On the client machine, run PowerShell as Administrator to execute the bootstrap script from [WPT releases](https://github.com/migasfree/windows-package-tool) ([windows-package-tool-installer](https://github.com/migasfree/windows-package-tool/releases)):
   ```bat
   tar -xf windows-package-tool_1.2.2_x64.tar.gz
   set WPT_INSTALL_DIR=C:\ProgramData\wpt\windows-package-tool
   python pms\install.py
   ```

   This script initializes the core package manager directories under `%PROGRAMDATA%\wpt\` and creates standard CLI aliases.
2. **Publishing the Suite on the Server**: Precompiled packages (`wpt`, `migasfree-client`, `migasfree-agent`, `migasfree-play`, and `lshw-windows-emulator`) are uploaded to a Windows project store.
   ```bash
   migasfree upload -f migasfree-client_5.0.0_x64.tar.gz -j Windows-11 -s base
   migasfree upload -f lshw-windows-emulator_1.0.0_x64.tar.gz -j Windows-11 -s base
   migasfree upload -f migasfree-agent_5.0.0_x64.tar.gz -j Windows-11 -s base
   migasfree upload -f migasfree-play_5.0.0_x64.tar.gz -j Windows-11 -s base
   ```
3. **Repository Configuration and Installation**: The client points its `sources.list` to the server and installs the full client suite with `wpt install migasfree-suite`.
   ```powershell
   # Configurar la fuente del repositorio (reemplazar <FQDN> y <PROYECTO>)
   Set-Content -Path "$env:PROGRAMDATA\wpt\sources.list" `
     -Value "https://<FQDN>/src/<PROYECTO>/REPOSITORIES/ migasfree"

   # Actualizar el catálogo e instalar los componentes
   wpt update
   wpt install migasfree-client lshw-windows-emulator migasfree-agent migasfree-play
   ```

### Basic WPT Operations

The WPT manager provides a clean, familiar syntax inspired by APT and DNF:

```powershell
# Buscar paquetes disponibles en el catálogo
wpt search migasfree

# Listar paquetes instalados y su estado
wpt list

# Actualizar todos los paquetes del sistema
wpt upgrade

# Desinstalar un paquete
wpt remove paquete-obsoleto
```

## The Triad

The three client components introduced in the previous chapter operate natively on Windows workstations:

### migasfree-client on Windows

The synchronization engine operates with the exact same convergence logic as on Linux:

* **Configuration**: `%PROGRAMDATA%\migasfree-client\migasfree.conf`.
* **mTLS Keystore**: `%PROGRAMDATA%\migasfree-client\mtls\` for certificates and keys.
* **Activity Log**: `%WINDIR%\temp\migasfree.log`.

To establish trust with the server in mTLS deployments, the server’s Root CA certificate must be installed in the Windows certificate store (`Cert:\LocalMachine\Root`).

```powershell
Import-Certificate -FilePath "C:\ruta\al\ca.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

If the server uses a self-signed certificate, import it using PowerShell before initiating the first synchronization.

```powershell
# Extraer e importar el certificado CA directamente del servidor (reemplazar <FQDN>)
openssl s_client -showcerts -connect <FQDN>:443 2>$null | openssl x509 -outform PEM > "$env:TEMP\migasfree-ca.crt"
Import-Certificate -FilePath "$env:TEMP\migasfree-ca.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

#### Automatic or Manual mTLS Provisioning

During initial synchronization (`migasfree sync`), the client performs automated enrollment:

1. Requests an enrollment token from the Manager service identifying itself with its hardware CID.
2. Downloads its machine certificate in `.p12` (PKCS#12) format.
3. Extracts and installs PEM keys in `%PROGRAMDATA%\migasfree-client\mtls\`.

If you prefer manual server-side key generation, keys can be copied directly to the keystore folder.

```powershell
# Importación manual del paquete de certificados mTLS
migasfree import-mtls C:\ruta\certificado-equipo.tar
```

Unattended periodic synchronization is scheduled via the Windows Task Scheduler (running `migasfree sync --quiet`).

### migasfree-agent: RDP and Service with NSSM

On Windows workstations, [migasfree-agent](https://github.com/migasfree/migasfree-agent) adds native support for Remote Desktop Protocol (RDP) tunneling over WebSockets.

To ensure the agent runs uninterruptedly in the background, it is registered as a Windows Service using [NSSM](https://nssm.cc/) (*Non-Sucking Service Manager*).

```powershell
# Registrar e iniciar migasfree-agent como servicio de sistema en Windows
nssm install migasfree-agent "C:\ProgramData\wpt\packages\migasfree-agent\data\migasfree-agent.exe"
nssm start migasfree-agent
```

### migasfree-play: Catalog Integrated into the Start Menu

[migasfree-play](https://github.com/migasfree/migasfree-play) installs on the workstation, creating its corresponding shortcuts in the Windows Start Menu and system tray.

## Hands-on Case Study

Let us see how to package and deploy a corporate web browser using WPT:

### Package Structure

A WPT package is organized into two primary directories: `pms/` (metadata and install scripts) and `data/` (application payload files):

```text
firefox-esr/
├── pms/
│   ├── metadata.json
│   ├── install.cmd
│   └── remove.cmd
└── data/
    ├── Firefox-Setup.exe
    └── config.ini
```

File `pms/metadata.json`:

```json
{
  "name": "firefox-esr",
  "version": "128.3.0",
  "description": "Navegador web Mozilla Firefox ESR corporativo",
  "maintainer": "Administrador <admin@tuorganizacion.com>",
  "specification": "1.0.0",
  "homepage": "https://www.mozilla.org"
}
```

Unattended Installation Script (`pms/install.cmd`):

```bat
@echo off
"%~dp0..\data\Firefox-Setup.exe" -ms /INI="%~dp0..\data\config.ini"
exit /b %ERRORLEVEL%
```

Uninstallation Script (`pms/remove.cmd`):

```bat
@echo off
if exist "%ProgramFiles%\Mozilla Firefox\uninstall\helper.exe" (
    "%ProgramFiles%\Mozilla Firefox\uninstall\helper.exe" /S
)
exit /b 0
```

### Building, Publishing, and Deploying

1. **Build the Package with WPT**: Run the `build` subcommand inside the package directory:
   ```powershell
   wpt build .\firefox-esr\
   ```

   WPT validates metadata and generates the archive `firefox-esr-128.0-win64.wpt`.
2. **Upload to Server**: Upload the package to the Windows project store via `migasfree upload`.
   ```bash
   migasfree upload -f firefox-esr_128.3.0_x64.tar.gz -j Windows-11 -s almacén
   ```
3. **Console Assignment**: Under *Deployments*, map `firefox-esr` to target Windows attributes.
4. **Automatic Convergence**: Upon next sync, the client downloads the package and executes the unattended installer.

## Troubleshooting

When administering Windows workstations, specific issues may arise:

#### Common Incident Diagnostics on Windows Clients

| Symptom or Error                    | Probable Cause                                                           | Corrective Action                                                                   |
|-------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `TLSV1_ALERT_UNKNOWN_CA`            | The server’s Root CA is not installed in the Windows trusted root store. | Import certificate `ca.crt` into `Cert:\LocalMachine\Root` using PowerShell.        |
| Error `404 Not Found` during sync   | Local cryptographic keys are out of sync with server records.            | Delete `%PROGRAMDATA%\migasfree-client\keys` and force a new synchronization.       |
| `403 Forbidden` on agent connection | Machine mTLS certificate invalid or revoked.                             | Delete `%PROGRAMDATA%\migasfree-client\mtls` and run `migasfree sync` to re-enroll. |
| `wpt search` returns no packages    | The repository URL in `sources.list` is incorrect or unreachable.        | Verify `%PROGRAMDATA%\wpt\sources.list` and check HTTP connectivity.                |

### Reference Paths on Windows Systems

* **WPT Base Directory**: `%PROGRAMDATA%\wpt\`
* **Repository Sources**: `%PROGRAMDATA%\wpt\sources.list`
* **Client Configuration**: `%PROGRAMDATA%\migasfree-client\migasfree.conf`
* **Machine mTLS Keystore**: `%PROGRAMDATA%\migasfree-client\mtls\`
* **Synchronization Log**: `%WINDIR%\temp\migasfree.log`
* **Package Manager Log**: `%TEMP%\wpt.log`

## Summary

Integrating Microsoft Windows into migasfree demonstrates the versatility and power of declarative architecture:

* **Hardware Homogeneity**: `lshw-windows-emulator` bridges WMI data into standardized XML telemetry.
* **Declarative Package Management**: `windows-package-tool` (WPT) provides isolated, reproducible software deployments on Windows.
* **Unified Experience**: From synchronization with `migasfree-client` to RDP remote assistance with `migasfree-agent` and self-service with `migasfree-play`, administrators manage Windows using the exact same workflows as GNU/Linux.

With client endpoints (both GNU/Linux and Windows) fully governed, in the next chapter we explore **Bare-Metal Mass Provisioning with MCS**.

# MCS

> > Everything should be made as simple as possible, but not simpler.

In [Chapter 15 (Master Images)](chapter15.md#imagenes-maestras) we explored how the server designs, builds, and publishes operating system images using the Golden Image as Code paradigm.

In the migasfree architecture, MCS is the component that works **on the bare metal of the target computer**: a lightweight live distribution engineered specifically to partition disks, stream raw blocks, render post-clone provisioning templates, and trigger automatic enrollment with the server.

Throughout this chapter we will examine how to obtain the boot medium, how to operate the terminal user interface (TUI), and how the unattended deployment pipeline functions.

#### NOTE
**The foundation is already set**: In Chapter 6 (Mass Provisioning) we experienced a complete hands-on deployment in a virtual machine. Here we focus on the underlying architecture and operational mechanics of MCS.

\

## Overview

MCS is a custom live distribution based on **Alpine Linux**, designed to execute in RAM with minimal memory footprint and instant boot times.

The complete bare-metal provisioning pipeline is articulated in two synchronized phases:

* **Compilation (CI)**: With MGI on the server, the master image is declared, compiled in containers or virtual machines, and published as a set of compressed `.raw` partition images in `/pool/mgi/`.
* **Deployment (CD)**: With MCS on the target machine, the system boots into RAM via USB or PXE, partitions the local drive, streams image blocks, executes the provisioning recipe, and leaves a fully functional workstation ready for user login.

Upon completing the imaging process, the computer reboots, automatically enrolls in migasfree, and converges with its assigned software deployments.

MCS also handles its own network connectivity autonomously: upon booting, it configures DHCP interfaces and validates HTTPS reachability to the server.

\

## Boot Medium

MCS is distributed as a pre-configured ISO image containing default server connection settings.

### Medium Structure

The boot medium uses a **GPT** partition table supporting both modern UEFI and legacy BIOS systems:

* **MCS_EFI**: EFI System Partition (*ESP*) loaded by UEFI firmware.
* **BIOS Boot**: Boot partition for GRUB on legacy BIOS / GPT systems.
* **MCS_ROOT**: The root filesystem of the Alpine Linux live environment loaded into RAM.
* **MCS_DATA**: Persistent data partition used to store downloaded local images, Wi-Fi credentials, and runtime settings.

In `MCS_DATA` resides the runtime configuration file `mcs.conf`, which can be modified directly from the TUI.

### Obtaining the Image

The MCS ISO image file (`mcs-<version>.iso`) is hosted directly in the public repository of your migasfree server:

```text
https://<FQDN_SERVIDOR>/pool/mcs/
```

### Preparing the USB Drive

To write the ISO to a USB flash drive of at least 4 GB (32 GB or larger recommended if storing local images), you can use graphical imaging tools such as [balenaEtcher](https://etcher.balena.io/) or [Rufus](https://rufus.ie/), or the command line utility on GNU/Linux:

```bash
sudo dd if=mcs-<version>.iso of=/dev/sdX bs=4M status=progress
```

 *(Ensure you replace \`\`/dev/sdX\`\` with the correct device node of your USB drive)*

#### NOTE
If using Rufus and prompted for image write mode, select **DD Image mode** rather than ISO mode. On first boot from the USB drive, MCS automatically expands its `MCS_DATA` partition to fill all available unallocated space on the flash drive, ready to store local master images.

\

## User Interface

When booting the target machine from the USB medium, you enter the text-based TUI menu of MCS, offering two imaging modes and maintenance utilities:

### Network Clone

Designed for **mass deployments** in corporate local area networks (or via PXE netboot). Streams the MGI image directly from the migasfree server to local disk via HTTP streaming (`wget | dd`). On Gigabit networks, this option is typically faster than USB 2.0 drives and guarantees workstations always receive the latest published image version.

### Local Clone

Designed for **remote branch offices or locations without network connectivity**. Clones an MGI master image stored locally in the `MCS_DATA` partition of the USB drive, deploying workstations completely offline at full hardware bus speeds.

### Local Images

Lists master images stored in the persistent `MCS_DATA` partition of the USB drive, allowing administrators to copy images from network shares or purge obsolete releases.

### Settings

Allows fine-tuning runtime environment parameters:

* **Connectivity and Security**: Modify the server URL, IP address, or Wi-Fi network credentials.
* **Promoted Images Filter**: For safety, newly compiled images are not promoted to production by default.
  * With **Promoted: true** (default behavior), MCS only displays production-promoted builds.
  * With **Promoted: false**, MCS unlocks and displays all builds, including experimental staging images for lab testing.

\

## Cloning

Cloning a master image onto a computer is executed through three sequential stages:

### Partition Scheme

The target disk layout is defined by the `partition.yml` file declared in the MGI configuration.

```yaml
partitions:
  - number: 1
    name: EFI
    size: 512
    filesystem: vfat
    mount: /boot/efi
  - number: 2
    name: SYSTEM
    size: 20480
    filesystem: ext4
    mount: /
  - number: 3
    name: HOME
    size: 0
    filesystem: ext4
    mount: /home
```

Three core rules govern this scheme:

* **Decoupling \`\`SYSTEM\`\` and \`\`HOME\`\`**: The base OS partition (`SYSTEM`) is isolated from user data (`HOME` or `DATA`).
* **Structural Naming**: Structural partitions (`BOOT`, `SYSTEM`, `HOME`, `SWAP`) allow MCS to apply intelligent preservation logic.
* **Dynamic Sizing**: A partition size of `0` instructs MCS to allocate all remaining unallocated disk space dynamically to that partition.

Furthermore, MCS automatically generates the target system’s `/etc/fstab` with exact filesystem UUIDs.

### User Data Preservation

Immediately before partitioning, MCS analyzes the target disk layout and checks if a valid `HOME` partition already exists:

* **Yes**: Only the operating system partition (`SYSTEM`) is overwritten; the user data partition (`HOME`) is preserved untouched.
* **No**: The entire disk is wiped, partitioned, and formatted from scratch.

For safety, if the destination disk is brand new or has an incompatible layout, MCS enforces a clean installation.

#### NOTE
**Centralized Administrator Security**: User data preservation enables rapid re-imaging of existing machines without risking personal files.

### Writing the Image

MCS reads `.raw` partition images and streams them directly onto disk block devices:

* **Over the Network**: The machine downloads compressed partition blocks in a continuous stream directly to disk.
* **From USB**: MCS streams partition blocks directly from the `MCS_DATA` filesystem to the local disk.

Because `.raw` images are stored shrunk to their minimum size and expanded to the full partition size at destination, imaging completes in minutes.

Block-level streaming guarantees a bit-by-bit identical copy of the verified Golden Image.

### Provisioning Script

A key architectural design principle of MCS is that **the imaging process must be completely unattended** from start to finish.

To achieve this while retaining per-machine customization, MCS uses parameterized Jinja2 provisioning scripts:

1. **Pre-imaging Parameter Prompt**: Before touching the disk, MCS prompts the technician for any required deployment parameters declared in script headers (such as hostname prefix or room number).
2. **Automatic Jinja2 Rendering**: Once block writing completes, MCS renders the provisioning script template with captured parameters.
3. **Chroot Execution**: MCS enters a chroot environment on the newly written disk and executes the rendered script to apply local customizations.

### Tag Injection and Cloning Timestamp

Every master image includes a static identity file, `/etc/migasfree-tags`, and a build audit record, `/etc/migasfree-golden-image.json`:

* **Tag Propagation**: MCS extracts flavour tags and writes them into the client system.
* **Cloning Timestamp**: MCS injects the exact deployment date and time into `/etc/migasfree-golden-image.json` for inventory traceability.

### Repository Integration

Master images compiled and published with MGI reside in the server’s public pool under `/pool/mgi/<template>/<release>/`.

```text
http://<FQDN_SERVIDOR>/pool/mgi/<NOMBRE_MGI>/
├── partition.yml        # Esquema de particiones (obligatorio)
├── provision.sh.j2      # Script de aprovisionamiento renderizado por MCS
├── checksums.sha256     # Sumas SHA-256 de integridad
├── SYSTEM.raw           # Imagen de la partición del sistema
└── HOME.raw             # Imagen de la partición de datos
```

At the root of the pool, the `catalog.json` manifest indexes all available configurations, flavours, releases, and partition checksums.

```json
[
  {"name": "fwm", "enabled": true,  "description": "Fun with migasfree"},
  {"name": "win10", "enabled": true, "description": "Windows 10 Enterprise"},
  {"name": "centos-7", "enabled": false, "description": "CentOS 7 (discontinuado)"}
]
```

SHA-256 cryptographic checksums are verified before writing blocks to guarantee data integrity.

## Summary

In this chapter we explored how **MCS** brings Master Images to physical hardware:

* **Autonomous, Versatile Medium**: A lightweight live Alpine Linux distribution supporting UEFI and BIOS boot.
* **Interface and Modes**: Seamless support for both mass network streaming (HTTP) and offline local USB deployment.
* **Intelligent Preservation**: Decoupling OS and user data partitions to re-image workstations while preserving `/home`.
* **Unattended Provisioning**: Pre-imaging parameter prompts, Jinja2 template rendering, chroot execution, and tag injection.

With the base OS deployed and the Client Triad ensuring continuous convergence, in the next chapter we explore **Data, Telemetry, and the AI-powered MCP Server**.

# Data

> > In God we trust; all others must bring data.

Having modeled configuration, software, and deployment in previous chapters, we reach the observatory of the migasfree console: the **Data** module.

Governing thousands of geographically distributed computers is impossible without reliable, continuous, and updated telemetry. An administrator must be able to answer questions such as:

* What exact hardware does each workstation have?
* Which computers have not synchronized for weeks or exhibit operational anomalies?
* Who is logged into each workstation and which department does it belong to?
* What version of each package is installed on which machines, and when was it installed or uninstalled?
* What proactive alerts or faults require immediate technician intervention?

The **Data** module constitutes the information, auditing, and observability core of migasfree, transforming raw telemetry reported during synchronizations into actionable intelligence.

Throughout this chapter we will explore each of its sections:

* The central inventory of **Computers** and its advanced views (hardware introspection, event maps, sync simulators, and barcode asset tags).
* Hardware replacement and decommissioning workflows via **Computer Replacement**.
* Software divergence analysis with the **Software Comparator** and package audit history (**Package History**).
* Session tracking and active user census (**Users**).
* The real-time catalog of **Attributes** and **Tags**.
* The operational log of **Synchronizations**, **Errors**, and proactive **Faults**.
* Lifecycle traceability through **Status Logs** and **Migrations**.
* Communication and alerting channels with **Messages** and **Notifications**.

\

## Overview

In migasfree there is a fundamental conceptual separation between two data realms:

1. **Configuration Data (Declarative Rules)**: What the administrator intends the fleet to be (Projects, Formulas, Deployments, Schedules, Policies).
2. **Operational Data (Real State and Telemetry)**: What *actually exists* on the machines (hardware inventories, installed packages, user sessions, errors, sync timestamps).

During each periodic synchronization, the migasfree client collects local telemetry and submits it to the server, updating the Data module tables in real time.

The operational goal of the system administrator must always be **convergence**: ensuring real operational state matches declared configuration state across 100% of the fleet.

### The System Alert Center

The alert center (accessible via the bell icon in the web console top navigation bar) acts as an early warning radar for the platform:

1. **Unchecked Errors**: Technical exceptions or package manager failures reported by client machines.
2. **Unchecked Faults**: Preventive anomalies detected by diagnostic formulas (e.g., low disk space, SMART disk warnings, failed backups).
3. **Unchecked Notifications**: Important administrative events generated by the server.
4. **Orphan Packages**: Packages uploaded to stores not currently assigned to any active deployment.
5. **Synchronizing Computers**: Endpoints actively communicating with the server right now.
6. **Delayed Computers**: Workstations exceeding their maximum allowed synchronization interval.
7. **Repository Generation**: Notifies if repository metadata indexers are running or pending rebuild.
8. **Active Staged Deployments**: Displays temporary rollout deployments currently executing modular schedule phases.
9. **Completed Staged Deployments**: Alerts to deployments that have reached 100% of the fleet and are ready for consolidation.

\

## Computers

*Data > Computers*

The **Computers** view is the master inventory of all workstations and servers governed by migasfree.

Each registered computer has an exhaustive technical record combining hardware specifications, network parameters, and software status.

### Main Fields

* **CID**: Unique, permanent numeric identifier assigned by the server upon enrollment (e.g., `CID-4821`).
* **UUID**: Universally unique hardware UUID of the motherboard reported by DMI/SMBIOS.
* **Name**: System hostname or configured `Computer_Name` override.
* **FQDN**: Fully Qualified Domain Name of the machine in the network DNS hierarchy.
* **Project**: Target operating system distribution the machine belongs to.
* **Status**: Operational lifecycle status of the workstation (e.g., *Assigned*, *Available*, *Reserved*, *Repair*, *Decommissioned*).
* **Machine Type**: Distinguishes between **Physical (P)** hardware or **Virtual (V)** machines.
* **IP Address / Forwarded IP**: Local LAN IP address and public gateway IP address.
* **MAC Address**: Physical MAC addresses of installed network adapters.
* **Base Hardware**: CPU model, total RAM memory in bytes, and primary storage drive capacity.
* **Sync User**: User account logged into the desktop during the last synchronization.
* **Tags**: Administrative labels manually assigned to the computer.
* **Sync Attributes**: Dynamic attributes calculated by formulas on the machine.
* **Timestamps**: Enrollment date (*created_at*) and last successful synchronization timestamp (*sync_date*).

### Lifecycle and Computer States

migasfree structures the six operational lifecycle states into two main categories:

| Category                   | State              | Operational Meaning and Behavior                                                    |
|----------------------------|--------------------|-------------------------------------------------------------------------------------|
| **ACTIVE: Productive**     | **Assigned**       | In normal production use. Receives all assigned deployments, updates, and policies. |
| **ACTIVE: Productive**     | **Reserved**       | Active production machine reserved for testing, events, or standby loaner pools.    |
| **ACTIVE: Productive**     | **Unknown**        | Newly registered machine awaiting administrative review and tag assignment.         |
| **ACTIVE: Non-Productive** | **Available**      | In storage/warehouse, unassigned, ready to be issued to a user or department.       |
| **ACTIVE: Non-Productive** | **Under Repair**   | Temporarily removed from service due to technical hardware failure.                 |
| **DECOMMISSIONED**         | **Decommissioned** | Permanently retired from service due to obsolescence, disposal, or loss.            |

#### NOTE
**Automatic Security Cleanup upon State Change:**

When a computer transitions to **Available** or **Decommissioned**, the server automatically strips all custom user tags and unlinks personal printers.

This prevents confidential department settings or printer queues from leaking when a machine is reassigned to another user.

### Advanced Computer Views

Inside the detail view of any computer, the console provides specialized operational panels:

1. **Hardware Inventory**: Structured hardware tree generated by `lshw` introspection.
2. **Events and Timeline**: Chronological log and visual activity calendar showing sync frequency and uptime patterns.
3. **Sync Simulator**: Interactive tool calculating which deployments, packages, and printers match the machine without running a physical sync.
4. **Remote Access and Remote Sync**: Launches on-demand SSH, VNC, RDP tunnels, or triggers background synchronizations via `migasfree-agent`.
5. **Asset Tag Barcode Generator**: Generates printable physical barcode asset tags containing CID, serial numbers, and QR codes.

\

## Computer Replacement

*Data > Computer Replacement*

When a computer suffers a catastrophic motherboard failure or is upgraded to new hardware, re-registering it as a new machine would lose its historical CID, package logs, and configuration tags.

The **Computer Replacement** tool solves this challenge atomically:

A technician takes a replacement machine from the warehouse in *Available* state and clones it using MCS.

1. The replacement computer boots on the network and registers as a temporary machine.
2. In **Computer Replacement**, the technician selects the failed original machine and the new replacement machine.
3. Upon clicking **Replace**, the server executes an atomic identity swap:
4. Transfers the original **CID**, tags, logical printer queues, and deployment rules to the new machine.
   * Swaps operational statuses between machines (the new machine becomes *Assigned*; the broken machine becomes *Available* or *Decommissioned*).
   * Finally, the technician can edit the defective machine to mark it *Under Repair* or decommission it.
   * On its next synchronization, the new computer assumes the exact identity and software profile of the original machine seamlessly.

Software Comparator

\

## *Data > Software Comparator*

The **Software Comparator** is a forensic analysis tool allowing administrators to compare installed software packages across multiple machines side by side.

Selecting two or more computers displays a comparative software matrix highlighting:

Common installed packages and their exact version parity.

* Packages present on one machine but absent on others.
* Version discrepancies between computers belonging to the same project.
* *Comparative software matrix between two workstations (Source vs Target)*

Package History

\

## *Data > Package History*

The **Package History** is the global ledger recording every software installation, update, and removal across the enterprise.

It provides instant answers to technical audit and compliance questions:

On what exact date was the web browser updated on workstation CID-4821?

* Which computers in the fleet still have an outdated package version installed?
* What software packages were installed or removed across the organization during the past week?
* Fields

### **Computer**: Workstation where the package installation or removal occurred.

* **Package**: Full package identifier.
* **Project**: OS project the package belongs to.
* **Install Date**: Timestamp when the package was installed.
* **Uninstall Date**: Timestamp when the package was removed.
* Users

\

## *Data > Users*

In migasfree it is helpful to distinguish between *console administrative users* (technicians) and *endpoint end users* (people logging into managed desktops).

The **Users** section maintains a dynamic census of all end-user accounts detected across workstations.

During each synchronization, the client reports the currently logged-in desktop user:

**Username (login)**: Account login username (e.g., `jdoe`, `profesor01`).

### **Computer**: Workstation where the package installation or removal occurred.

* **Full Name**: User’s real name obtained from the local system or LDAP/Active Directory.
* Attributes

\

## *Data > Attributes*

The **Attributes** view provides the consolidated catalog of all dynamic attributes generated across the fleet.

Clicking any attribute in the list instantly filters all computers currently possessing that attribute.

**Formula**: Configuration formula that evaluated and generated the attribute.

### **Computer**: Workstation where the package installation or removal occurred.

* **Prefix**: Three-letter taxonomic namespace prefix (e.g., `HW_`, `NET_`, `OS_`).
* **Value**: Specific runtime value emitted by the formula on the endpoint.
* **Description**: Optional notes explaining the functional meaning of the attribute.
* **Location (Add Coordinates)**: Allows assigning geographic latitude and longitude coordinates to the attribute for mapping views.
* Tags

\

## *Data > Tags*

The **Tags** view provides the census of all administrative and organizational tags assigned to computers.

Unlike attributes (which are computed dynamically by formula scripts), tags are managed manually by administrators or toggled via `migasfree-play`.

**Tag Category**: Taxonomic category the tag belongs to (e.g., `Department`, `Floor`).

### **Computer**: Workstation where the package installation or removal occurred.

* **Value**: Tag name or code (e.g., `ACCOUNTING`, `ROOM-101`).
* **Description**: Summary of the tag’s purpose and scope.
* **Computers**: List of computers currently holding this tag.
* **Location (Add Coordinates)**: Allows geolocating the tag on interactive maps.
* Synchronizations

\

## *Data > Synchronizations*

Every time a migasfree client communicates with the server, a detailed synchronization transaction log is recorded.

In a standard environment, synchronizations trigger automatically at boot, user login, periodic timers, or on demand via `migasfree sync`.

**Start Date**: Exact timestamp when the sync session began.

### **Computer**: Workstation where the package installation or removal occurred.

* **End Date**: Timestamp when the transaction completed.
* **User**: User account logged into the machine during the sync.
* **Computer**: Workstation that executed the synchronization.
* **Project**: Operating system project evaluated during sync.
* **PMS Status**: Return code and status of the native package manager execution (`OK`, `ERROR`).
* **Consumer**: migasfree client software version that executed the sync.
* Delayed Computers

### The server continuously audits synchronization logs: any computer exceeding its configured maximum synchronization interval triggers a delayed computer alert in the alert center.

Errors

\

## *Data > Errors*

An **Error** represents an unexpected technical exception occurring during client synchronization (e.g., network timeout, package manager lock, script syntax error).

The error log preserves the full Python traceback and OS return codes for rapid diagnostics.

**Checked?**: Checkbox toggled by technicians once an incident is reviewed and resolved.

### **Computer**: Workstation where the package installation or removal occurred.

* **Timestamps**: Date and time when the error occurred.
* **Computer**: Client workstation where the error was captured.
* **Project**: Project assigned to the affected machine.
* **Description**: Full error traceback or technical message.
* Faults

## *Data > Faults*

A **Fault** represents a **preventive functional anomaly detected proactively** on an endpoint (e.g., low disk space on `/var`, SMART disk error, backup failure).

**Checked?**: Checkbox toggled by support staff once remediation is performed.

### **Computer**: Workstation where the package installation or removal occurred.

* **Timestamps**: Date and time of fault detection.
* **Fault Definition**: Name of the proactive diagnostic check that triggered.
* **Computer**: Client workstation that reported the fault.
* **Result**: Diagnostic output emitted by the check script detailing the anomaly.
* **Description**: Full error traceback or technical message.
* Status Logs

\

## *Data > Status Logs*

The **Status Log** is the permanent audit trail recording every transition in a computer’s operational lifecycle.

**Date**: Exact timestamp when the state transition occurred.

### **Computer**: Workstation where the package installation or removal occurred.

* **Computer**: Affected workstation (identified by CID and hostname).
* **Status**: New operational status adopted by the machine (*Assigned*, *Available*, *Decommissioned*).
* Chronologically reviewing these records reconstructs the complete historical lifecycle of any physical asset in the organization.

Migrations

\

## *Data > Migraciones*

The **Migrations** view records the history of operating system project migrations across the fleet (e.g., workstations upgrading from `Debian-11` to `Debian-12`).

When a workstation changes its project setting in `migasfree.conf`, the server detects the transition and logs a permanent migration entry.

**Date**: Exact timestamp when the migration was recorded.

### **Computer**: Workstation where the package installation or removal occurred.

* **Computer**: Migrated workstation (identified by CID and hostname).
* **Project**: New destination operating system project.
* Messages

\

## *Data > Messages*

The **Messages** view streams real-time progress messages emitted by client machines during active synchronizations.

As the client advances through convergence phases (mTLS negotiation, attribute calculation, package downloads, driver installation), it broadcasts brief status updates.

This provides administrators with real-time visibility into fleet activity without having to wait for sync completion.

**Date**: Timestamp when the client emitted the message.

### **Computer**: Workstation where the package installation or removal occurred.

* **Computer**: Workstation executing synchronization.
* **Project**: Operating system project.
* **User**: Active logged-in user account.
* **Message**: Status string describing current sync phase.
* Notifications

\

## *Data > Notifications*

The **Notifications** view displays administrative alerts generated automatically by server background workers (e.g., repository index builds, automated backups, new computer enrollments).

**Date**: Exact timestamp when the notification was created.

### **Computer**: Workstation where the package installation or removal occurred.

* **Checked**: Indicates whether an administrator has acknowledged the alert (*Yes* or *No*).
* **Message**: Explanatory text describing the server event.
* Summary

\

## In this chapter we explored the data, telemetry, and observability architecture of migasfree:

**Computers and Replacement**: Maintaining a live hardware and software inventory of the fleet with atomic hardware replacement workflows.

* **Software Auditing**: The **Software Comparator** and **Package History** provide granular package-level forensic traceability.
* **Activity and Tracking**: Continuous tracking of **Users**, **Attributes**, **Tags**, **Synchronizations**, **Status Logs**, and **Migrations**.
* **Proactive Maintenance and Security**: Early incident detection through **Errors**, proactive **Faults**, **Messages**, **Notifications**, and the **Alert Center**.
* With this chapter we conclude Part III (Administration & Operation). Next, we enter **Part IV: Integration and Extensibility**.

With this chapter we conclude the **Administration** block (Part III) of migasfree, having explored in detail the server architecture, the web console, and its five major operational modules (**Configuration**, **Devices**, **Release**, **Master Images**, and **Data**).

Let us take a brief pause on our journey. Fancy a refreshing drink? After mastering the platform machinery and observability mechanisms, the time has come to take the definitive leap into production. Take a breath and recharge: in **Part IV** we will tackle key strategies, best practices, and critical aspects to deploy migasfree in production with total confidence.

# IV. Production

Reaching production represents the true test of maturity for any systems management platform. A real corporate environment subjects the infrastructure to stresses that rarely manifest in a laboratory: thousands of workstations synchronizing simultaneously at the start of the workday, unexpected node failures, saturation of WAN links in remote offices, and the unavoidable requirement to maintain business continuity without interruption.

In this **Part IV**, we place ourselves in the perspective of the system architect and operator to address the principles, architectures, and procedures that guarantee robust, scalable, and secure operation of migasfree in the real world.

Throughout the next three chapters we will explore:

* **Chapter 20 (High Availability)**: You will learn how to size the necessary resources according to the size of the client base, optimize traffic in remote sites with local caches, and design multi-node topologies in Docker Swarm with NFS storage. Likewise, you will configure PostgreSQL in high availability with Pgpool-II to guarantee read balancing and transparent auto-failover.
* **Chapter 21 (Operation)**: You will discover how to shield your data through comprehensive backup strategies (PostgreSQL, Redis, and NFS), execute disaster recovery plans, and apply rolling updates to the stack with zero downtime.
* **Chapter 22 (Observability)**: You will master the preventive philosophy of zero alerts, the operational consoles panel (/status), real-time log traceability, AI-assisted diagnosis through the MCP server, and cryptographic debugging and validation tools on client workstations.

Get ready to transform your migasfree server into a solid, resilient infrastructure ready to govern client groups of any scale.

# High Availability

> > Everything fails, all the time.

In previous chapters we explored server internal components (Chapters 9 and 10) and management tools governing workstations, packages, and master images. However, taking the leap into production requires answering critical systems engineering questions:

* How much CPU and RAM memory does the server require to manage 2,000, 10,000, or 50,000 computers?
* How should network and storage architectures be designed so that a single hardware failure does not interrupt service?
* How do we guarantee that the PostgreSQL database comfortably handles thousands of concurrent synchronizations?
* How do we isolate internal services to meet enterprise cybersecurity standards?

In this chapter you will learn capacity planning guidelines, Docker Swarm multi-node deployment topologies, database high availability strategies with [Pgpool-II](annex05-glossary.md#term-Pgpool-II), and perimeter security models to operate migasfree in production with total confidence.

\

## Sizing

Capacity planning for a migasfree cluster depends primarily on three operational variables:

1. **Fleet Size**: Total number of computers registered in the system.
2. **Synchronization Concurrency**: Number of workstations contacting the server within the same time window (typically concentrated at the start of the workday or school morning).
3. **Package Volume and MGI Builds**: Frequency of PMS repository index generation and Master Image build jobs.

### Indicative Capacity Sizing Profiles

Because concurrency patterns and software volume vary across organizations, the following table provides **theoretical guidelines** as a starting reference for infrastructure planning:

| Profile              | Fleet Size     | Minimum CPU         | Minimum RAM              |
|----------------------|----------------|---------------------|--------------------------|
| Shared Storage (NFS) | Topology       | **Small**           | < 2,000                  |
| 4 vCPUs              | 8 GB           | 100 GB (SSD / NVMe) | Single Node / Standalone |
| **Medium**           | 2,000 - 10,000 | 100 GB (SSD / NVMe) | 8 vCPUs                  |

### 16 - 32 GB

500 GB (NFS SSD)

Multi-node Swarm (1 Manager + 1 Worker)

* **Large**
* 10,000 - 50,000

16+ vCPUs

1. 64+ GB
2. 2 TB+ (NFS / NetApp / Ceph)

### Multi-node Swarm (1 Manager + N Workers)

Network Bandwidth Consumption Model

Network traffic in migasfree is cleanly divided into two distinct communication channels:

**Data Traffic (Package Downloads & MGI Images)**: Heavy binary transfers through the web server / reverse proxy. Payload size depends directly on deployed packages (e.g., a 120 MB LibreOffice update).

1. For example, in a fleet of 5,000 computers synchronizing in a 30-minute morning window:
   ```bash
   sudo apt update
   sudo apt install apt-cacher-ng
   ```
2. API and telemetry requests account for only **~75 MB** across the entire window.

   Package transfers, however, will download over **600 GB** of binary data.
   ```text
   // File /etc/apt/apt.conf.d/01proxy (10.20.0.1 is the local cache IP)
   Acquire::http::Proxy "http://10.20.0.1:3142";
   ```

To prevent WAN saturation and ISP bandwidth bottlenecks, migasfree employs two complementary strategies:

* **Temporal Rollout via Schedules** (*Schedule Delay* using Modular Arithmetic MID): Phasing updates over days or weeks.
* **Local Remote Branch Caching Proxies**: Distributing package downloads locally at branch offices.

\

## Package Caching in Remote Branches

In organizations with multiple geographical locations (such as schools, bank branches, or regional offices), downloading heavy packages over WAN links across hundreds of local PCs saturates internet connectivity.

### migasfree control communication with the server must always remain direct (mTLS), but binary package downloads can be cached locally using a simple HTTP proxy (such as `squid`, `nginx`, or `apt-cacher-ng`).

*Local cache for package downloads in remote branch offices*

* To optimize package download traffic exclusively:
* **Service Installation**:
* **Client Configuration**:

### Configure APT on branch workstations—via a migasfree configuration deployment—to route package downloads through the local caching proxy:

Optimized download workflow:

The **remaining 49 computers** request the same package: the local proxy serves it at LAN wire speed without consuming WAN bandwidth.

1. Topologies
2. migasfree v5 is orchestrated natively on **Docker Swarm**, enabling deployment topologies ranging from single-node instances to distributed enterprise clusters.
   * Topology 1: Single Node Server (Small and Medium Environments)
   * In environments up to 5,000 computers, all microservices run containerized on a single physical or virtual host.
   * **Advantages**: Minimal operational complexity, lower hardware overhead.
3. **Configuration**: In `cluster.conf` set `DATASHARE_FS='LOCAL'`.

\

## **Limitation**: The host constitutes a single point of failure (SPOF) if hardware malfunctions.

Topology 2: Multi-node Cluster

### For enterprise environments, the standard architecture deploys a multi-node Swarm cluster:

*Multi-node migasfree topology with role segregation and shared NFS storage*

1. Three core architectural principles govern this topology:
   ```bash
   sudo apt install nfs-kernel-server
   sudo mkdir -p /exports/migasfree-swarm
   ```
2. **Cluster Governance**: In the current suite version, the cluster topology is deployed with **1 Swarm Manager node** and **N Worker nodes**.
   ```text
   /exports/migasfree-swarm 192.168.10.0/24(rw,sync,no_subtree_check,anonuid=0,anongid=0)
   ```

   * **Workload Segregation and Distribution**:
   * **Distributed and Load-Balanced Services**: Transactional APIs (`core`, `manager`) and PMS indexers scale dynamically across worker nodes.
   * **Global Mode Services**: The ingress proxy (`proxy` with HAProxy) runs in global mode across every node in the cluster.
3. **Manager Node Constraints**: State-sensitive services (such as `celery-beat` scheduler or database containers) are pinned to the Manager node.
   ```bash
   sudo exportfs -ra
   sudo systemctl restart nfs-kernel-server
   ```
4. **Decoupled Persistent Storage**: Shared data (stores, repositories, master images, TLS keys) is hosted on centralized network storage (NFS / SAN / NAS).
   ```bash
   # Permitir el tráfico NFS únicamente desde las IPs de los nodos del clúster
   nodes=("192.168.10.11" "192.168.10.12" "192.168.10.13")
   for node in "${nodes[@]}"; do
       sudo ufw allow from "$node" to any port nfs
   done
   ```

#### TIP
Storage

In a multi-node cluster, stateless worker containers execute on any host, requiring access to a single shared storage mount.

### NFS Server Configuration

The NFS server should be installed on a dedicated storage host or high-availability NAS:

```bash
sudo apt install nfs-common
```

### **Install Service and Create Export Directory**:

**Configure Permissions in \`\`/etc/exports\`\`**:

1. **rw**: Grants read and write access to all cluster nodes.
   ```bash
   migasfree-swarm undeploy-all
   ```
2. **sync**: Guarantees disk write confirmation before replying to network requests.
   ```bash
   DATASHARE_FS='nfs'
   DATASHARE_SERVER='192.168.10.50'
   DATASHARE_PATH='/exports/migasfree-swarm'
   DATASHARE_PORT='2049'
   ```
3. **anonuid=0, anongid=0**: Maps anonymous NFS access to root UID/GID for container consistency.
   ```bash
   migasfree-swarm deploy
   ```
4. **Apply and Verify Service**:

\

## **Firewall Rules on NFS Server**:

**Eliminating SPOF in Enterprise Storage:**

In large deployments, the NFS backend should be backed by hardware RAID, dual controllers, or distributed storage systems (NetApp, TrueNAS HA, Ceph, GlusterFS).

| Preparing Cluster Nodes   | On **every** node in the Swarm cluster, install NFS client utilities:                      | Automated Migration from Local Storage to NFS                                                                 | If you started your deployment on a single server with local storage and wish to transition to shared NFS:                              |
|---------------------------|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Stop all stack services:  | Edit `cluster.conf` and update configuration parameters:                                   | Run the deploy command:                                                                                       | The deployment script automatically detects the storage mode change and migrates existing data from local directories to the NFS mount. |
| Database                  | The PostgreSQL database engine constitutes the transactional heart of the entire platform. | migasfree provides **three deployment strategies** controlled by the `POSTGRES_HOST` setting in `stack.conf`: | Strategy                                                                                                                                |
| POSTGRES_HOST             | Deployed Services                                                                          | Target Scenario                                                                                               | **Direct Internal**                                                                                                                     |

`'database'`

#### WARNING
Direct `database` container

Single-node test and development environments only.

### **High Availability**

`'pgpool'`

**Production standard** in multi-node clusters.

1. **External Database**
2. `'10.0.0.50'` or `'db.company.com'`

\

## No internal DB containers

Managed cloud databases (AWS RDS, Cloud SQL) or dedicated PostgreSQL HA clusters.

### To configure an **External Database**, simply set `POSTGRES_HOST` to the external IP/hostname in `stack.conf`.

**Risk in Multi-node Direct Internal Mode:**

* In a multi-node cluster, running `POSTGRES_HOST='database'` without Pgpool is unrecommended because database queries cannot be load-balanced across replicas.
* High Availability Strategy with Pgpool-II
* In the High Availability strategy, the `database` service runs with read replicas while `pgpool` manages connection pooling and query routing:
* *Routing and query load-balancing flow with Pgpool-II and PostgreSQL replicas*

### Operational advantages of Pgpool-II in migasfree:

**Read-Only Query Balancing**: Intensive telemetry queries (monitoring, dashboards, API reads) are distributed across read replicas, leaving the primary database dedicated to writes.

| **Connection Pooling**: Reuses established database connections, preventing thread exhaustion during concurrent sync spikes.                                  | Security                                                                                                                                                       | Governing thousands of enterprise workstations demands a rigorous, defense-in-depth security model.                                                   |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Port Isolation and Internal Networks                                                                                                                          | In migasfree v5, external exposure strictly adheres to the principle of least privilege:                                                                       | **Exposed Public Ports (HAProxy)**: Only ports **80 (HTTP)** and **443 (HTTPS/WSS)** are exposed externally.                                          |
| **Isolated Overlay Networks**: All internal microservices communicate exclusively across encrypted private Swarm overlay networks (`internal_net`, `db_net`). | **Management Console Access Restrictions (NETWORK_MNG and NETWORK_PLAY)**: Restricts access to administrative endpoints to authorized management CIDR subnets. | **Saturating Traffic and DDoS Rate Limiting (RATE_LIMIT)**: HAProxy enforces connection rate limiting per source IP to prevent API denial-of-service. |

The Hybrid Certificate Model

#### NOTE
migasfree implements a dual cryptographic architecture separating web traffic from device mTLS:

Scope

\

## Certificate Type

Purpose and Behavior

* **Public / Web** (Frontend & APIs)
* Public SSL/TLS certificate (Let’s Encrypt or Corporate CA)
* Allows administrators to access the web console and users to browse public documentation without browser trust warnings.
* **Private / Devices** (Client mTLS)
* mTLS certificates issued by the internal migasfree private CA
* Guarantees **mutual authentication**: the server cryptographically validates the hardware identity of every connecting computer.

Thanks to this separation, renewing public web certificates has zero impact on client mTLS communication.

# Operations

> > By failing to prepare, you are preparing to fail.

Once the migasfree cluster is properly sized and in active service, the operations team’s responsibility focuses on three fundamental pillars:

1. **Guarantee data resilience**: Ensure that in any contingency or infrastructure disaster, data loss is zero through atomic backups.
2. **Restore service in catastrophic scenarios**: Apply fast, tested recovery protocols to restore full platform state within minutes.
3. **Evolve the platform with zero downtime**: Apply software updates, security patches, and microservice redeployments without service interruptions.

In this chapter, we will cover the procedures, commands, and best practices to operate and maintain migasfree day to day with confidence.

\

## Backups

In migasfree, there are two distinct persistence planes that must be backed up with appropriate techniques:

1. **Transactional Plane (In-memory and disk databases)**:
   * **PostgreSQL (Database)**: Hosts relational tables of computers, projects, deployments, package history, formulas, attributes, policies, and users.
   * **Redis (Datastore)**: Records Celery asynchronous task states, messages in flight, active sessions, and supervision timers (*watchdogs*).
2. **Static Storage Plane (\*Datashare\* / NFS)**:
   * Corporate software packages and generated repositories (APT, RPM, APK).
   * Operating system golden master images (MGI) and cloning ISO images (MCS).
   * Cryptographic certificates of the migasfree Certificate Authority (CA).

### Automated Backups with migasfree-swarm

The `migasfree-swarm` orchestrator includes an automated backup engine programmable via the `BACKUP_CRON` variable in the `stack.conf` configuration file (by default, executed every night at 00:00 h):

```python
# Scheduled backup frequency in stack.conf
BACKUP_CRON = '0 0 * * *'
```

During each dump cycle, the system atomically generates two files on the cluster shared volume (accessible at `/exports/migasfree-swarm/<STACK>/dump/` or via browser at `https://datashare.<FQDN>/files/dump/`):

* **\`\`migasfree.sql\`\`**: Full PostgreSQL relational dump generated via `pg_dump` with minimal read locks (the process itself automatically executes a `VACUUM` cleanup).
* **\`\`migasfree.rdb\`\`**: Consolidated binary snapshot of the Redis database.

### Generating Manual Backups

Before performing any major infrastructure intervention (such as upgrading to a new major version or server hardware maintenance), the administrator can trigger an immediate manual dump via the `migasfree-swarm` command-line interface:

```bash
# 1. Generate default backup (overwrites migasfree.sql and migasfree.rdb)
migasfree-swarm backup mi-stack

# 2. Generate a tagged backup with a specific timestamp
migasfree-swarm backup mi-stack 2026-08-18-previo-actualizacion
```

The command will create the `2026-08-18-previo-actualizacion.sql` and `2026-08-18-previo-actualizacion.rdb` files in the dump directory.

### NFS Shared Storage Backup

To complete the platform’s full backup, the shared directory must be backed up **directly on the NFS server itself** (using open-source backup utilities like BorgBackup or Restic, or via SAN/ZFS storage snapshots):

```bash
# Run on the NFS server: Incremental backup to external storage
rsync -aAXv --delete /exports/migasfree-swarm/ /mnt/backup-externo/migasfree-swarm/
```

\

## Restore

If a catastrophic database storage failure or severe data corruption occurs, the restore protocol allows bringing the service back online and restoring the complete state within minutes.

### Step-by-Step Restore Procedure

To restore a backup without client traffic interference and in a completely safe manner, the procedure consists of three steps executed from the *Manager* node:

1. **Step 1: Stop the proxy service**: By temporarily removing the global `proxy` service, ports 80 and 443 are immediately closed across all cluster nodes. No clients can connect or sync, while internal database (PostgreSQL) and datastore (Redis) services remain active on Swarm virtual networks:
   ```bash
   docker service rm mi-stack_proxy
   ```
2. **Step 2: Execute dump restoration**: Run the `restore` command specifying the stack name (and optionally the desired dump tag). The process will terminate residual active connections, recreate the PostgreSQL database from the `.sql` file, and load the Redis snapshot from the `.rdb` atomically:
   ```bash
   # Restore default dumps (migasfree.sql and migasfree.rdb)
   migasfree-swarm restore mi-stack

   # Or restore a specific historical dump
   migasfree-swarm restore mi-stack 2026-08-18-previo-actualizacion
   ```
3. **Step 3: Redeploy the stack and restore traffic**: Reapply the stack deployment. Docker Swarm will recreate the `proxy` container on all nodes within seconds, resuming normal client handling:
   ```bash
   migasfree-swarm deploy mi-stack
   ```

#### NOTE
If the incident involved total physical loss of shared storage (NFS), remember to first restore the `/exports/migasfree-swarm` directory from your external backup prior to invoking restoration, ensuring the availability of files in `dump/` and CA certificates.

### Restore Verification and the 3-2-1 Rule

A backup that has never been restored is not trustworthy. Schedule **periodic restore testing** (for example, restoring volumes in a test environment or at least validating dump integrity) and follow the **3-2-1 rule**: at least **3 copies** of the data, on **2 different media**, with **1 copy located off-site**.

\

## Upgrades

One of the major benefits of the microservice architecture on Docker Swarm in migasfree v5 is the ability to apply software upgrades with **zero downtime**.

The cluster web manager (`migasfree manager`) continuously monitors the availability of newly published releases. When an update is available, the **TAG** badge on the top bar displays a red notification dot warning that the cluster is not running the latest published version.

The upgrade procedure consists of two phases: pre-downloading images across all nodes and applying the live rolling update.

1. **Pre-download new Docker images on all nodes**: To guarantee instantaneous container replacement without uneven download times between machines, new images must be pre-pulled on each node. Click on the red dot on the **TAG** in the top panel to open the *Pre-download images on all nodes* wizard. After entering Portainer credentials, the system will centrally pull all images on all nodes (*Manager* and *Workers*).
2. **Apply the rolling update from the Manager node**: Once all nodes have the new images downloaded, update the orchestrator and launch deployment from the *Manager* node:
   ```bash
   # Run ONLY on the Manager node
   wget -O - http://migasfree.org/pub/install-swarm | bash
   migasfree-swarm deploy mi-stack
   ```

When running deployment, an instant **rolling update** is performed:

1. Starts a new container with the updated image alongside the old container.
2. Verifies that the internal healthcheck responds successfully (HTTP 200).
3. Redirects HAProxy traffic towards the new container.
4. Gracefully stops and destroys the old container.

If the new container fails during startup, Swarm aborts the operation and keeps traffic on the previous container, preventing any service disruption. After deployment completes, the web panel automatically refreshes the **TAG** in real time and the red indicator disappears.

### Restarting and Redeploying a Single Service

If you wish to restart or force an update of a specific microservice without touching the rest of the stack, use the `redeploy` command:

```bash
# Redeploy only the APT repository generation service (PMS)
migasfree-swarm redeploy pms-apt
```

\

## Summary

In this chapter, we explored the operational pillars for maintaining migasfree in production:

* **Backups**: Automation of PostgreSQL relational dumps and Redis snapshots via `migasfree-swarm backup`, complemented by NFS data backups.
* **Disaster recovery**: Standardized three-step protocol using `migasfree-swarm restore` to bring the service back up following severe incidents within minutes.
* **Upgrades**: Progressive, zero-downtime rolling updates leveraging Docker Swarm microservice orchestration.

In the next chapter, we will conclude this block by exploring platform **Observability**.

# Observability

> > What cannot be measured cannot be improved. And what is not improved always degrades.

In a production environment with thousands of computers synchronizing daily, administrators cannot afford to work blindly: when a workstation fails to receive a package, a client fails to self-register, or a microservice experiences slowdowns, observability tools are essential to diagnose the root cause within seconds.

To achieve effective management, observability in migasfree is structured across two complementary planes: **platform observability** (operations and SRE level, focused on server microservices, databases, and transport) and **fleet observability** (application and business level, focused on workstation health).

In this chapter, you will learn to:

* Apply the **“Zero Alerts”** philosophy as your first line of daily operational defense.
* Enable and interpret **diagnostic web consoles** on the server (HAProxy, Flower, pgAdmin, RedisInsight, Swagger, and Portainer) with consoles-dev and consoles-pro.
* Extract and analyze **execution traces and real-time logs** from Docker Swarm services.
* Monitor **fleet functional health** and audit incidents in natural language using the **MCP server and Artificial Intelligence**.
* Diagnose **client workstations in debug mode**, validate mTLS cryptographic identities, and audit migasfree-agent remote tunnels.

\

## Zero Alerts

Observability does not start when a service crashes or a user reports an issue; the first line of defense in migasfree is **proactive daily monitoring**.

The migasfree dashboard incorporates a real-time **Alert Center** compiling technical deviations occurring across the fleet:

* **Server alerts**: Failures in PMS index generation, stores with orphan packages, or certificates close to expiration.
* **Computer alerts**: Proactive faults detected by client scripts, APT/RPM package errors, IP address collisions, or computers that have stopped syncing.

#### NOTE
**The golden rule of proactive support**: The administration team must consult the dashboard daily at the start of the day. Any alert must be investigated, resolved, and marked as **checked**. Keeping the counter at **zero alerts** prevents small latent issues from accumulating and turning into major incidents.

\

## Platform

The operations plane concentrates on server monitoring, container health in Docker Swarm, database performance, and proxy transport throughput.

### Live Diagnostic Consoles

As we saw in [Chapter 10](chapter10.md#stack), the central web console accessible at `https://<FQDN_SERVER>/status` offers an overarching view of microservice health and real-time synchronization metrics.

To intervene and diagnose deep platform issues, the `migasfree-swarm` orchestrator allows scaling auxiliary consoles (pgAdmin, RedisInsight, and Flower) on demand to 1 replica by running from the *Manager* node:

```bash
migasfree-swarm consoles-dev
```

Once technical troubleshooting is complete, it is a good security and resource-saving practice in production to return them to inactive state (0 replicas):

```bash
migasfree-swarm consoles-pro
```

Main operational consoles for diagnostics:

1. **HAProxy Stats (Proxy Status)**: Offers real-time metrics on active connections, requests per second (req/s), response times in milliseconds, and backend status for `core`, `manager`, and 

   ```
   ``
   ```

   tunnel\*\*.
2. **Flower (Celery Queue Management)**: Monitors migasfree background workers, displaying running asynchronous tasks, repository indexing success rates, and retries.
3. **pgAdmin and RedisInsight (Databases)**: Allow inspecting SQL query performance, locks in PostgreSQL, replica status in Pgpool-II, and memory usage in Redis.
4. **Filebrowser (Storage Explorer)**: Web interface to browse backup dump directories (`dump/`), golden master images (`pool/mgi/`), and packages.
5. **Swagger UI (REST API Explorer)**: Live OpenAPI documentation to test REST endpoints and verify HTTP response codes interactively.
6. **Portainer (Container and Swarm Management)**: Provides a full graphical UI to supervise cluster service health, view live container logs, and open interactive terminal sessions on the fly.

### Traceability and Log Inspection

Docker Swarm centralizes standard output (*stdout*) and error (*stderr*) streams from all containers in the swarm. The `docker service logs` command allows following the activity of any component live:

```bash
# 1. Follow migasfree Core logs in real time (Django / Uvicorn)
docker service logs -f mi-stack_core

# 2. Inspect package repository manager logs (PMS)
docker service logs -f mi-stack_pms-apt

# 3. View the last 100 lines of the reverse proxy log
docker service logs --tail 100 mi-stack_proxy

# 4. Inspect remote tunnel server activity
docker service logs -f mi-stack_tunnel
```

Key metrics to watch in logs:

* **Memory usage in the PMS**: During massive indexing of large repositories, metadata calculation may require temporary RAM spikes.
* **Synchronization API response times**: In proxy logs, requests to `/api/v1/safe/synchronizations/` should typically resolve in under **200 ms**. Times over 2 seconds indicate database connection saturation or contention in complex formulas.

To prevent container logs from consuming disk space on cluster nodes over time, it is recommended to configure automatic log rotation in the `/etc/docker/daemon.json` file of each host machine:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  }
}
```

\

## Fleet

The application plane focuses on the health of the managed fleet: whether workstations are correctly converging towards their desired state, which deployment policies are being applied, and where functional errors concentrate.

### Fleet Health and Status

From the migasfree web interface, the administration team oversees fleet health through three direct workflows:

1. **Delayed computer detection**: On the top bar, the **Alert Center** displays a real-time counter of *Delayed computers* (machines that have exceeded the maximum unsynced threshold). Clicking on the alert—or navigating to **Data > Computers** and applying date filters—yields the exact list of powered-off, disconnected, or communication-impaired machines.
2. **Convergence and deployment auditing**: To verify the application of software policies across the fleet:
   * **Deployment progress**: In the **Release > Deployments** menu, each scheduled deployment includes a temporal progress bar (*ScheduleProgress*) reflecting percentage completion according to schedule.
   * **Workstation simulation**: In the header of any computer card (**Data > Computers**), the **Simulate synchronization** action runs the workstation’s formulas and attributes live, breaking down the exact list of applicable deployments and packages.
   * **Software inventory**: The **Software** tab on the computer card displays the catalog of packages currently installed and reported by the client.
3. **Fault and execution error inspection**: When a package manager (APT, DNF/YUM, Pacman, APK) returns an error exit code or an audit script detects a local anomaly, the event is classified on the dashboard:
   * **Unchecked faults**: Functional or hardware anomalies captured by local scripts.
   * **Unchecked errors**: Critical failures during workstation synchronization processes.

   Clicking on the alert (or browsing to **Data > Errors** or **Data > Faults**) allows inspecting the full terminal trace emitted by the client to diagnose root causes.

### AI-Assisted Diagnostics (MCP)

In fleets with thousands of computers, traditional troubleshooting often involves analyzing dozens of relational tables or writing complex SQL queries to correlate failures across package versions, attributes, and timestamps.

The [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) integrated into migasfree allows modern AI assistants (such as Antigravity, Claude Desktop, or Cursor) to act as real-time observability analysts, querying the database via a read-only user account:

```text
Revisa los fallos de sincronización registrados en las últimas 6 horas.
Identifica qué equipos han fallado, qué paquete ha provocado el error
y resume los motivos principales agrupados por proyecto.
```

The assistant analyzes the relational schema, crafts a read-only SQL query, and generates a structured report with an executive incident summary:

#### NOTE
For full MCP server architecture, tools catalog, and step-by-step connection guides, see [Annex: AI Assistant Integration](annex03-mcp-integration.md#anexo-mcp).

\

## Client

When a computer does not apply expected directives or shows anomalous behavior, the administrator has three local and remote diagnostic techniques to complete the observability loop:

### 1. Running the Client in Debug Mode

Running `migasfree` with the `--debug` switch (or `-u -d`) displays in the terminal exhaustive details of each convergence protocol stage:

```bash
# Run synchronization in debug mode with maximum verbosity
sudo migasfree --debug sync
```

The output will detail each synchronization cycle phase:

* Configuration and execution options (server, project, certificate path, and environment).
* Formula code retrieval, evaluation, and upload of computer attributes.
* Retrieval, execution, and reporting of fault definitions (*faults*).
* Key download, repository configuration, and PMS metadata synchronization.
* Resolution and execution of mandatory packages to install or purge, plus system upgrades.
* Retrieval and configuration of logical devices (such as printers and drivers).
* Upload of software inventory and consolidation of features assigned to the computer.

### 2. Verifying mTLS Cryptographic Identities

Certificates identifying the computer to each configured server are stored in the protected directory `/var/migasfree-client/mtls/<server>/` (e.g., `/var/migasfree-client/mtls/migasfree.acme.com/`):

* **\`\`ca.pem\`\`**: Public Certificate Authority (CA) certificate of migasfree.
* **\`\`cert.pem\`\`**: Public client certificate (contains the computer identifier in `UUID_CID` format in its *Common Name*).
* **\`\`key.pem\`\`**: Private client key (with restrictive `0600` permissions).

We can verify client certificate identity and validity by inspecting its *Subject*:

```bash
# Inspect the Common Name (UUID_CID) and certificate validity
openssl x509 -in /var/migasfree-client/mtls/migasfree.acme.com/cert.pem -noout -subject -dates
```

And verify mutual authentication (mTLS) and the TLS *handshake* against the server using `curl`:

```bash
# Test mTLS negotiation with the server
curl -v --cacert /var/migasfree-client/mtls/migasfree.acme.com/ca.pem \
     --cert /var/migasfree-client/mtls/migasfree.acme.com/cert.pem \
     --key /var/migasfree-client/mtls/migasfree.acme.com/key.pem \
     https://migasfree.acme.com/api/v1/public/keys/repositories/
```

We know mTLS negotiation succeeded because:

* The TLS trace shows `SSL certificate verify ok` and completes the handshake without cryptographic alerts.
* The server accepts the client identity and responds with an HTTP `200 OK` code.
* The response body returns the JSON object containing the repositories’ public key.

### 3. Diagnosing Remote Tunnels with migasfree-agent

If the workstation rejects remote SSH, VNC, or RDP connections from the web console, check the tunnel service status:

```bash
# Check the service status on Linux
sudo systemctl status migasfree-agent

# Or inspect live service logs
sudo journalctl -u migasfree-agent -f
```

\

## Summary

With this chapter, we conclude the **Production** block (Part IV) of migasfree:

* **Zero Alerts Philosophy**: Daily monitoring of the alert center enables detecting and resolving anomalies before they escalate into major incidents.
* **Fleet Observability**: Functional monitoring and AI-powered audits via the MCP server to troubleshoot census incidents in natural language.
* **Platform Observability**: Live diagnostic consoles (HAProxy, Flower, pgAdmin, RedisInsight) and centralized log tracing in Docker Swarm.
* **Client Workstation Diagnostics**: Debugging utilities (`--debug`, mTLS validation, and `migasfree-agent` logs) enable systematic isolation of local issues.

#### TIP
To view step-by-step solutions to common production errors and issues (502/504 errors, NTP clock skew, 403 errors, or PMS indices), consult the updated FAQ directly through MCP server queries.

In the next part, we will delve into advanced configuration **Settings**, both on the server and on the client workstation, to maximize the performance and flexibility of migasfree.

# V. Settings

Mastering a systems management platform at a large scale does not only consist of knowing its day-to-day commands, but in understanding precisely which settings and parameters allow for tuning its behavior in each of its components. From container infrastructure and server services to workstation clients and desktop tools, migasfree offers a modular, clean, and extensible configuration architecture.

In this **Part V**, we gather the comprehensive guide of settings, variables, and configuration directives for the migasfree ecosystem, organized as an operational and technical reference manual:

#### NOTE
This part is the **canonical source** of migasfree configuration. The narrative chapters ([Chapter 10](chapter10.md#stack) and [Chapter 16](chapter16.md#entorno-cliente)) describe the architecture and operation; all directives with their default values are consolidated here, so that the tables in this part take precedence over any other mention in the book.

* **Chapter 23 (Server)**: We will examine in detail the configuration files of the Swarm cluster (`cluster.conf` and `stack.conf`), covering networks, perimeter security, mTLS, PostgreSQL and Redis databases, replica sizing, PMS services, sync saturation control, and the secure override mechanism for directives in the migasfree backend. It will close with practical guidance by client-base profiles to choose the appropriate value in each case.
* **Chapter 24 (Client)**: We will analyze the directives of the client configuration file (`migasfree.conf`), the data paths and scheduled execution with systemd, the extension points and lifecycle *hooks* (`pre-sync.d`, `post-sync.d`, `events.d`), the environment variables and parameters of migasfree-play, and the secure execution control lists in migasfree-agent.

# Server

> Order and simplification are the first steps toward the mastery of a subject.

Proper sizing and operational stability of migasfree depend on how the various infrastructure layers are configured. A production deployment is not a static block: it requires calibrating network parameters, saturation thresholds, access policies, database engine, and backend settings to match organizational scale.

In this chapter, we will analyze in depth all server and migasfree-swarm orchestration configuration files, structured across three fundamental layers:

1. **The infrastructure and cluster layer** (`cluster.conf`).
2. **The service stack and orchestration layer** (`stack.conf`).
3. **The backend layer** (`settings.py`).

While in [Chapter 10 (Stack)](chapter10.md#stack) you learned the purpose of each service, here you will find the details of each directive, its default value, and practical guidance for choosing the right values for your fleet profile.

\

## Cluster

The `cluster.conf` file defines global storage properties and shared data support across the Docker Swarm cluster. This file resides on the manager node and is consulted during infrastructure deployment and initialization.

* **Standard location on manager node**: `/etc/migasfree-swarm/cluster.conf`

### Storage Directives

The migasfree infrastructure requires a shared storage space (*datashare*) hosting package repositories, stores, backups, and mTLS certificates.

| Variable           | Technical Description                                                                                                                                                   |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `DATASHARE_FS`     | Type of shared filesystem. Supported values: `local` (for single-node or lab environments) and `nfs` (for multi-node production clusters).  *(Default: \`\`local\`\`)*. |
| `DATASHARE_SERVER` | IP address or fully qualified domain name of the NFS server exporting shared volumes.  *(Mandatory when \`\`DATASHARE_FS=nfs\`\`)*.                                     |
| `DATASHARE_PATH`   | Absolute path exported on the NFS server where data for all stacks will reside.  *(Default: \`\`/exports/migasfree-swarm\`\`)*.                                         |
| `DATASHARE_PORT`   | TCP/UDP network port used for communication with the NFS service.  *(Default: \`\`2049\`\`)*.                                                                           |

### Production Configuration Example

In a high-availability cluster with network storage, `cluster.conf` adopts the following structure:

```ini
# /etc/migasfree-swarm/cluster.conf
DATASHARE_FS="nfs"
DATASHARE_SERVER="192.168.10.50"
DATASHARE_PATH="/srv/nfs/migasfree-cluster"
DATASHARE_PORT="2049"
```

#### NOTE
If `DATASHARE_FS="local"` is selected, migasfree-swarm will use local directories on the manager node (typically under `/var/lib/docker/volumes/`), which disables data container mobility across different compute nodes.

\

## Stack

Each service stack deployed in migasfree-swarm has its own `stack.conf` file. This file governs operational behavior, networking, security, and container sizing for that specific instance.

* **Location in Datashare console**: `/stack.conf` (at the root of the stack volume).

Below, we detail its directives grouped by operational domains.

### Identity, Network, and General Access

These govern public identity and ingress ports of the HAProxy edge load balancer:

| Variable     | Description                                                                                                                                                                           |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `STACK`      | Identifying name of the stack. Assigned during initial deployment; do not modify manually.                                                                                            |
| `FQDN`       | Fully qualified domain name through which clients and administrators access the server.  *(Default: \`\`migasfree.acme.com\`\`)*.                                                     |
| `FQDN_IP`    | IP address automatically captured from the host’s `/etc/hosts` file. Useful in dev environments or networks without a DNS server. If empty, standard DNS resolution is used.          |
| `TZ`         | Time zone applied to all stack containers to synchronize timestamps.  *(Default: \`\`Europe/Madrid\`\`)*.                                                                             |
| `PORT_HTTP`  | Port on which the cluster listens for incoming HTTP requests.  *(Default: \`\`80\`\`)*.                                                                                               |
| `PORT_HTTPS` | Port on which the cluster listens for secure HTTPS requests.  *(Default: \`\`443\`\`)*.                                                                                               |
| `RATE_LIMIT` | Maximum number of requests permitted within a 10-second window from the same IP and URL before returning an anti-DDoS HTTP 429 (*Too Many Requests*) code.  *(Default: \`\`100\`\`)*. |

### Edge Security and Certificates

| Variable      | Description                                                                                                                                                                                                                                         |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `HTTPSMODE`   | TLS certificate issuance and management mode. Supported options: `manual` (custom or locally generated self-signed certificates) or `auto` (automatic issuance and renewal via Let’s Encrypt ACME HTTP-01 challenge).  *(Default: \`\`manual\`\`)*. |
| `MTLS`        | When set to `True`, HAProxy requires mutual TLS authentication via browser X.509 client certificate to access administrative consoles and APIs.  *(Default: \`\`False\`\`)*.                                                                        |
| `NETWORK_MNG` | Space-separated list of IP addresses or CIDR networks authorized to access administrative consoles (Flower, pgAdmin, RedisInsight, HAProxy Stats).  *(Default: \`\`0.0.0.0/0\`\`)*.                                                                 |
| `NETWORK_MCP` | Addresses authorized to communicate with the MCP (*Model Context Protocol*) server. Restricted to local access (`127.0.0.1`) by default.                                                                                                            |

#### WARNING
In production environments exposed to open networks, always restrict `NETWORK_MNG` to your corporate management subnets to prevent public exposure of consoles.

### PostgreSQL Database and Replication

These directives control connections to the relational database engine and the Pgpool-II cluster:

| Variable                | Description                                                                                                                                                                                                                                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `POSTGRES_HOST`         | Database engine connection mode. Internal options: `pgpool` (high-availability gateway with read/write splitting) or `database` (direct single-node connection). If an external IP or FQDN is provided, internal services are not deployed and the remote host is connected to.  *(Default: \`\`pgpool\`\`)*. |
| `POSTGRES_PORT`         | Internal communication port for PostgreSQL or Pgpool.  *(Default: \`\`5432\`\`)*.                                                                                                                                                                                                                             |
| `PORT_DATABASE`         | Port published in *host* mode on cluster nodes. Required when using Pgpool-II with static IPs so the gateway can reach database nodes across the Swarm cluster.  *(Default: \`\`5432\`\`)*.                                                                                                                   |
| `POSTGRES_DB`           | Name of the main application database.  *(Default: \`\`migasfree\`\`)*.                                                                                                                                                                                                                                       |
| `POSTGRES_USER`         | Owner user of the migasfree database.  *(Default: \`\`migasfree\`\`)*.                                                                                                                                                                                                                                        |
| `REPLICATION_USER`      | Technical user used for streaming physical replication connections.  *(Default: \`\`repuser\`\`)*.                                                                                                                                                                                                            |
| `POSTGRES_PRIMARY_NODE` | Name of the Swarm cluster node acting as primary write node for PostgreSQL.  *(Default: \`\`node-1\`\`)*.                                                                                                                                                                                                     |
| `POSTGRESQL_CONF`       | Pipe-separated list of configuration parameters injected into `postgresql.conf` (e.g., `work_mem=64MB|max_connections=100`).  *(Default: \`\`work_mem=32MB\`\`)*.                                                                                                                                             |

### In-Memory Datastore (Redis)

| Variable     | Description                                                                                                                                                                   |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `REDIS_HOST` | Host of the Redis service. In standard setups, `datastore` is used; if using an external server outside the cluster, specify its IP or FQDN.  *(Default: \`\`datastore\`\`)*. |
| `REDIS_PORT` | Connection port to the Redis service.  *(Default: \`\`6379\`\`)*.                                                                                                             |
| `REDIS_DB`   | Logical database index within the Redis instance.  *(Default: \`\`0\`\`)*.                                                                                                    |

### Scalability and Replica Sizing

Allows configuring the number of running instances for each stack microservice:

| Variable                     | Microservice Function                                                                                         |
|------------------------------|---------------------------------------------------------------------------------------------------------------|
| `REPLICAS_core`              | Instances of the synchronization engine and core business logic (FastAPI / backend).  *(Default: \`\`1\`\`)*. |
| `REPLICAS_public`            | Nginx web servers for serving static files and package repositories.  *(Default: \`\`1\`\`)*.                 |
| `REPLICAS_worker`            | Celery background workers responsible for asynchronous processing.  *(Default: \`\`1\`\`)*.                   |
| `REPLICAS_tunnel`            | TCP/WebSocket tunnel relay servers for mTLS remote access.  *(Default: \`\`1\`\`)*.                           |
| `REPLICAS_console`           | Administrative management web frontend (Vue/Quasar frontend).  *(Default: \`\`1\`\`)*.                        |
| `REPLICAS_database_console`  | pgAdmin 4 console.  *(Default: \`\`1\`\` in development, set to \`\`0\`\` in production)*.                    |
| `REPLICAS_datastore_console` | RedisInsight console.  *(Default: \`\`1\`\` in development, set to \`\`0\`\` in production)*.                 |
| `REPLICAS_worker_console`    | Celery Flower console.  *(Default: \`\`1\`\` in development, set to \`\`0\`\` in production)*.                |

### Packaging Services, Maintenance, and Proxies

| Variable             | Description                                                                                                                                                                                                    |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `PMS_ENABLED`        | Comma-separated list of package managers enabled on the server. Allows restricting managers based on distributions present in the fleet.  *(Default: \`\`pms-apt, pms-yum, pms-pacman, pms-apk, pms-wpt\`\`)*. |
| `TUNNEL_CONNECTIONS` | Maximum concurrent connection capacity of the multi-protocol relay tunnel (recommended between 10000 and 65000 with `ulimit -n 524288` in production).  *(Default: \`\`50000\`\`)*.                            |
| `BACKUP_CRON`        | Standard crontab syntax scheduling daily dumps of PostgreSQL and Redis databases (at midnight).  *(Default: \`\`00 00 \* \* \*\`\`)*.                                                                          |
| `HTTP_PROXY`         | HTTP proxy URL used for outbound connections during image and ISO building (e.g., `http://proxy.acme.com:8080`).  *(Default: empty)*.                                                                          |
| `HTTPS_PROXY`        | HTTPS proxy URL for outbound connections during build tasks.  *(Default: empty)*.                                                                                                                              |
| `NO_PROXY`           | Comma-separated list of hostnames or IP addresses that should bypass the proxy (e.g., `localhost,127.0.0.1,.acme.com`).  *(Default: empty)*.                                                                   |
| `HAS_KEYBOARD`       | Determines if the runtime environment has interactive keyboard/console input.  *(Default: \`\`true\`\`)*.                                                                                                      |

### Saturation Control and Queuing (Anti-Collapse Strategy)

These directives regulate concurrency when thousands of clients synchronize simultaneously, guaranteeing prompt responses without degrading the database engine:

| Variable                      | Behavior and Operational Thresholds                                                                                                                 |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `SYNC_MAX_DB_LATENCY`         | Maximum allowed database latency (seconds). If exceeded, incoming requests are automatically queued.  *(Default: \`\`0.5\`\`)*.                     |
| `SYNC_MAX_CORE_LOAD`          | Maximum CPU load percentage on `core` instances before considering the node saturated and diverting traffic to the queue.  *(Default: \`\`90\`\`)*. |
| `SYNC_MAX_CONCURRENCY`        | Maximum number of concurrent synchronizations processed simultaneously from the queue.  *(Default: \`\`50\`\`)*.                                    |
| `SYNC_QUEUE_PROCESS_INTERVAL` | Interval in seconds with which the dispatcher checks and drains queued requests.  *(Default: \`\`30\`\`)*.                                          |
| `METRICS_RECORDING_INTERVAL`  | Performance metrics sampling frequency in the cluster (seconds).  *(Default: \`\`15\`\`)*.                                                          |
| `METRICS_RETENTION_LIMIT`     | Metrics retention duration in Redis memory (4 hours).  *(Default: \`\`14400\`\`)*.                                                                  |
\

## Backend

The migasfree backend, built on Django and FastAPI, features a set of operational settings defined in its internal configuration package (`migasfree/settings/`).

### Configuration Override (settings.py)

Rather than modifying server source code, migasfree allows customizing both [standard Django (5.2) directives](https://docs.djangoproject.com/en/5.2/ref/settings/) (SMTP email, authentication, logging…) and migasfree-specific constants via an external override file:

* **Location in Datashare console**: `/conf/settings.py`

### Computer Registration and Lifecycle

These constants govern how the backend admits, catalogs, and inventories workstations:

| Directive                           | Default Value and Operational Purpose                                                                                                                         |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `MIGASFREE_AUTOREGISTER`            | **Default**: `True`. Allows new clients contacting the server for the first time to automatically register into inventory.                                    |
| `MIGASFREE_DEFAULT_COMPUTER_STATUS` | **Default**: `'assigned'`. Initial status assigned to new computers. Options: `assigned`, `reserved`, `unknown`, `in repair`, `available`, or `unsubscribed`. |
| `MIGASFREE_HW_PERIOD`               | **Default**: `30`. Interval in days after which the client re-gathers and uploads the complete hardware inventory.                                            |
| `MIGASFREE_INVALID_UUID`            | **Default**:  *(list of UUIDs)*. List of clone or factory-defective motherboard UUIDs that migasfree invalidates to avoid collisions.                         |
| `MIGASFREE_COMPUTER_SEARCH_FIELDS`  | **Default**: `('id', 'name')`. Fields used to index and search computers in public API queries.                                                               |

### Corporate Identity and Support

Defines contact info, branding, and visual notification timeout intervals:

| Directive                         | Default Value and Operational Purpose                                                                     |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------|
| `MIGASFREE_ORGANIZATION`          | **Default**: `'My Organization'`. Corporate name displayed in headers, reports, and public interfaces.    |
| `MIGASFREE_HELP_DESK`             | **Default**:  *(Contact text)*. Informative message, email, or support link displayed to users on error.  |
| `MIGASFREE_SECONDS_MESSAGE_ALERT` | **Default**: `1800`. Expiration timeout in seconds (30 minutes) for active dashboard messages and alerts. |

### Automatic Change Notifications

The server can automatically log and alert administrators upon changes in workstation identity or connectivity:

| Directive                       | Monitored Event (Default: False)                                                        |
|---------------------------------|-----------------------------------------------------------------------------------------|
| `MIGASFREE_NOTIFY_NEW_COMPUTER` | Alerts upon onboarding and registration of a new workstation.                           |
| `MIGASFREE_NOTIFY_CHANGE_UUID`  | Alerts if the computer’s motherboard or UUID changes compared to the registered value.  |
| `MIGASFREE_NOTIFY_CHANGE_NAME`  | Alerts if the operating system hostname is renamed.                                     |
| `MIGASFREE_NOTIFY_CHANGE_IP`    | Alerts if the computer contacts the server reporting a different IP address than usual. |

### Scripting Languages for Properties and Faults

The `MIGASFREE_PROGRAMMING_LANGUAGES` variable defines supported code interpreters to evaluate dynamic property formulas and fault diagnostic scripts:

```python
# Intérpretes soportados en /conf/settings.py
MIGASFREE_PROGRAMMING_LANGUAGES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
    (5, 'cmd'),
    (6, 'powershell'),
)
```

### Cryptography and Key Names

Identifies public and private key files (hosted in the internal key store) used for package signing and cryptographic security:

| Directive                    | Default File and Purpose                                                                           |
|------------------------------|----------------------------------------------------------------------------------------------------|
| `MIGASFREE_PUBLIC_KEY`       | **File**: `'migasfree-server.pub'`. RSA/JWT public key of the server.                              |
| `MIGASFREE_PRIVATE_KEY`      | **File**: `'migasfree-server.pri'`. RSA/JWT private key of the server.                             |
| `MIGASFREE_PACKAGER_PUB_KEY` | **File**: `'migasfree-packager.pub'`. Public key for package verification.                         |
| `MIGASFREE_PACKAGER_PRI_KEY` | **File**: `'migasfree-packager.pri'`. Private key for digitally signing packages and repositories. |

### Microservices, Paths, and Rate Limiting

| Directive                            | Default Value and Purpose                                                                                          |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `MIGASFREE_MANAGER_URL`              | **Default**: `'http://manager:8080'`. Address of the FastAPI Manager microservice for tunnels and remote commands. |
| `MIGASFREE_STORE_TRAILING_PATH`      | **Default**: `'stores'`. Relative subdirectory for file stores and deployments.                                    |
| `MIGASFREE_REPOSITORY_TRAILING_PATH` | **Default**: `'repos'`. Relative subdirectory for software package repositories.                                   |
| `MIGASFREE_EXTERNAL_TRAILING_PATH`   | **Default**: `'external'`. Relative subdirectory for external resources and repositories.                          |
| `MIGASFREE_TMP_TRAILING_PATH`        | **Default**: `'tmp'`. Internal temporary subdirectory.                                                             |
| `API_V4_REGISTER_RATE_LIMIT_MAX`     | **Default**: `50`. Allowed registration requests for v4 clients within the time window.                            |
| `API_V4_REGISTER_RATE_LIMIT_WINDOW`  | **Default**: `30`. Time window in seconds for registration rate calculation.                                       |

### Integrated External Actions (MIGASFREE_EXTERNAL_ACTIONS)

Allows embedding custom buttons and shortcuts in the migasfree web console to interact with computers directly from the browser:

```python
# Ejemplo de configuración de acciones remotas en /conf/settings.py
MIGASFREE_EXTERNAL_ACTIONS = {
    "computer": {
        "ping": {"title": "PING", "description": "Comprobar conectividad ICMP"},
        "ssh": {"title": "SSH", "description": "Conexión remota por consola segura"},
        "vnc": {"title": "VNC", "description": "Control remoto gráfico", "many": False},
        "sync": {"title": "SYNC", "description": "Forzar sincronización remota (migasfree sync)"},
        "install": {
            "title": "INSTALL",
            "description": "Instalar un paquete remoto",
            "related": ["deployment", "computer"],
        },
    },
    "error": {
        "clean": {"title": "Limpiar", "description": "Eliminar historial de fallos"},
    },
}
```

## Guidance by Deployment Profiles

With so many directives, a quick guide on which variables to adjust based on fleet characteristics is essential. The following recommendations complement the hardware sizing covered in [Part IV (Production)](part04.md#iv-produccion):

| Fleet Scenario                                                    | Directives to Review                                                                 | Practical Recommendation                                                                                                      |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Homogeneous fleet** (Debian/Ubuntu only)                        | `PMS_ENABLED`                                                                        | Limit active managers to `'pms-apt'`: fewer services, smaller attack surface.                                                 |
| **Thousands of workstations syncing at the start of the workday** | `SYNC_MAX_*`, `METRICS_RECORDING_INTERVAL`                                           | Increase `SYNC_MAX_CONCURRENCY` and monitor latency with `SYNC_MAX_DB_LATENCY`: the queue strategy will protect the database. |
| **Server exposed to the Internet**                                | `HTTPSMODE`, `MTLS`, `NETWORK_MNG`, `RATE_LIMIT`                                     | Use `HTTPSMODE='auto'` (Let’s Encrypt) or `'self-signed'`, enable mTLS, and restrict management networks to your subnets.     |
| **Administrators connecting from a private subnet**               | `NETWORK_MNG`                                                                        | Replace `127.0.0.1` with the corporate subnet (e.g. `192.168.1.0/24`).                                                        |
| **Remote branches with slow WAN**                                 | `TUNNEL_CONNECTIONS`, `BACKUP_CRON`                                                  | Size the tunnel for expected concurrency and schedule backups during off-peak hours.                                          |
| **Unneeded development consoles**                                 | `REPLICAS_database_console`, `REPLICAS_datastore_console`, `REPLICAS_worker_console` | Set them to `0` in production to free memory.                                                                                 |
| **High notification and audit volume**                            | `MIGASFREE_*` (backend), `POSTGRESQL_CONF`                                           | Tune `MIGASFREE_HW_PERIOD` and change alerts, and optimize `work_mem`.                                                        |

## Summary

In this chapter, the canonical reference for server configuration, we covered the three adjustment layers of migasfree:

* **Cluster** (`cluster.conf`): Shared storage backing repositories, backups, and certificates (`DATASHARE_*`).
* **Stack** (`stack.conf`): Networking, edge security and mTLS, database and replicas, Redis, replica sizing, PMS, and saturation control.
* **Backend** (`settings.py`): Customization of constants, auto-registration, notifications, and external actions.

With the server tuned, only the final link in the chain remains: the client workstation. In the next chapter, we will cover the complete client configuration reference, from `migasfree.conf` to `migasfree-agent` whitelists.

Let’s dive in.

# Client

> The best way to predict the future is to invent it.

Both workstations and managed servers are the destination where policies, configurations, and deployments orchestrated in migasfree come to life. Their local components provide the flexibility needed to adapt to any scenario: isolated computers behind a proxy, remote branch nodes with constrained links, or periodic hardware audits.

In this chapter, you will see in detail the settings and directives of the three fundamental components that coexist on client machines:

1. **The synchronization and inventory client** (`migasfree-client`).
2. **The application catalog graphical interface** (`migasfree-play`).
3. **The secure remote access and tunnel agent** (`migasfree-agent`).

\

## migasfree-client

`migasfree-client` governs attribute negotiation with the server, dynamic repository management, software installation, and hardware inventory collection. All its behavior is defined in the `migasfree.conf` file.

### Configuration File Location

The default location of the file depends on the operating system:

* **GNU/Linux**: `/etc/migasfree.conf`
* **Microsoft Windows**: `%PROGRAMDATA%\migasfree-client\migasfree.conf` (e.g., `C:\ProgramData\migasfree-client\migasfree.conf`).

#### TIP
It is possible to override the configuration file path at any time by defining the `MIGASFREE_CONF` environment variable prior to invoking client commands.

### Directives in the [client] Section

The primary `[client]` section contains the following operational directives:

| Parameter              | Technical Description                                                                                                                                                                                                         |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Server`               | Address of the migasfree server. Supports simple format (`migasfree.example.com`, where HTTPS is assumed), full URL (`https://migasfree.example.com:8443`), or HTTP for development.  *(Default: \`\`https://localhost\`\`)*. |
| `Project`              | Name of the deployment project. If unspecified, the client auto-detects the base OS distribution and version (e.g., `Debian-12` or `Ubuntu-24.04`).  *(Autodetected)*.                                                        |
| `Auto_Update_Packages` | When enabled (`True`), the client automatically updates packages during the regular synchronization process (`migasfree sync`).  *(Default: \`\`True\`\`)*.                                                                   |
| `Manage_Devices`       | Enables automatic management and configuration of peripheral devices and printers on the computer.  *(Default: \`\`True\`\`)*.                                                                                                |
| `Upload_Hardware`      | Enables physical collection and upload of hardware inventory to the server.  *(Default: \`\`True\`\`)*.                                                                                                                       |
| `Computer_Name`        | Overrides the computer’s logical name in the migasfree database, regardless of the network hostname returned by `platform.node()`.  *(Default: OS Hostname)*.                                                                 |
| `Debug`                | Enables detailed execution logging and trace outputs in log files.  *(Default: \`\`False\`\`)*.                                                                                                                               |
| `Proxy`                | Address and port of the corporate HTTP proxy server (e.g., `192.168.1.100:8080`).  *(Default: none)*.                                                                                                                         |
| `Package_Proxy_Cache`  | Address and port of the local or branch package caching server (e.g., `192.168.1.101:3142` with *apt-cacher-ng*).  *(Default: none)*.                                                                                         |

### Directives in the [packager] Section

This optional section stores packaging credentials for the `migasfree-upload` command:

| Parameter   | Function                                                                                        |
|-------------|-------------------------------------------------------------------------------------------------|
| `User`      | User with packager permissions on the migasfree server.  *(Prompted via CLI if not specified)*. |
| `Password`  | Password of the packager user.  *(Prompted via CLI if not specified)*.                          |
| `Project`   | Default target project for package uploads.  *(Prompted via CLI if not specified)*.             |
| `Store`     | Software store where generated binaries will be placed.  *(Prompted via CLI if not specified)*. |

### Complete Example of migasfree.conf

```ini
# /etc/migasfree.conf
[client]
Server = https://migasfree.acme.com
Project = Debian-12
Auto_Update_Packages = True
Manage_Devices = True
Upload_Hardware = True
Package_Proxy_Cache = 192.168.10.20:3142
Debug = False

[packager]
User = packager_admin
Project = Debian-12
Store = default
```

### Environment Variables (MIGASFREE_\*)

`migasfree-client` allows overriding any configuration directive via environment variables. This capability is especially useful in containerized deployments, continuous integration (CI/CD) pipelines, or one-off command-line tests without modifying the system’s `migasfree.conf` file.

| Environment Variable                    | Directive and Purpose                                                                       |
|-----------------------------------------|---------------------------------------------------------------------------------------------|
| `MIGASFREE_CONF`                        | Overrides the absolute path to the `migasfree.conf` file.                                   |
| `MIGASFREE_CLIENT_SERVER`               | Equivalent to `[client] Server`. Server URL or FQDN.                                        |
| `MIGASFREE_CLIENT_PROJECT`              | Equivalent to `[client] Project`. Assigned project name.                                    |
| `MIGASFREE_CLIENT_COMPUTER_NAME`        | Equivalent to `[client] Computer_Name`. Logical name for the computer.                      |
| `MIGASFREE_CLIENT_AUTO_UPDATE_PACKAGES` | Equivalent to `[client] Auto_Update_Packages`. Automatic updates (`True` / `False`).        |
| `MIGASFREE_CLIENT_MANAGE_DEVICES`       | Equivalent to `[client] Manage_Devices`. Peripheral management (`True` / `False`).          |
| `MIGASFREE_CLIENT_UPLOAD_HARDWARE`      | Equivalent to `[client] Upload_Hardware`. Physical inventory submission (`True` / `False`). |
| `MIGASFREE_CLIENT_PROXY`                | Equivalent to `[client] Proxy`. HTTP proxy server (`host:port`).                            |
| `MIGASFREE_CLIENT_PACKAGE_PROXY_CACHE`  | Equivalent to `[client] Package_Proxy_Cache`. Cache proxy server (`host:port`).             |
| `MIGASFREE_CLIENT_DEBUG`                | Equivalent to `[client] Debug`. Detailed debug traces (`True` / `False`).                   |
| `MIGASFREE_PACKAGER_USER`               | Equivalent to `[packager] User`. Packager user for uploading.                               |
| `MIGASFREE_PACKAGER_PASSWORD`           | Equivalent to `[packager] Password`. Packager user password.                                |
| `MIGASFREE_PACKAGER_PROJECT`            | Equivalent to `[packager] Project`. Target project for packaging.                           |
| `MIGASFREE_PACKAGER_STORE`              | Equivalent to `[packager] Store`. Target store for uploaded packages.                       |

#### Precedence Order

When a parameter is defined across multiple sources, the client applies the following resolution order (highest to lowest priority):

1. **Environment variables** (highest priority, override any other value).
2. **Command-line arguments** (parameters passed directly to the CLI).
3. **Configuration file** (directives read from `migasfree.conf`).
4. **Internal default values** (fallback mechanism in the absence of configuration).

```bash
# Ejemplo: Sincronización puntual contra un servidor de pruebas en modo debug
MIGASFREE_CLIENT_SERVER=https://test.migasfree.org MIGASFREE_CLIENT_DEBUG=True sudo migasfree sync

# Ejemplo: Subida automatizada de paquetes en un pipeline de CI/CD
MIGASFREE_PACKAGER_USER=ci_bot MIGASFREE_PACKAGER_PASSWORD=secret migasfree upload -f pkg.deb
```

### Data Paths and System Logs

The client keeps its working directories and logs organized by platform:

| Item               | System Storage Paths                                                                                                           |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Log file           | **GNU/Linux**: `/var/tmp/migasfree.log`<br/><br/>**Windows**: `%WINDIR%\temp\migasfree.log`                                    |
| Software inventory | **GNU/Linux**: `/var/tmp/installed_software.txt`<br/><br/>**Windows**: `%PROGRAMDATA%\migasfree-client\installed_software.txt` |
| Machine attributes | **GNU/Linux**: `/var/tmp/computer_traits.json`<br/><br/>**Windows**: `%PROGRAMDATA%\migasfree-client\computer_traits.json`     |
| mTLS certificates  | **GNU/Linux**: `/var/migasfree-client/mtls/`<br/><br/>**Windows**: `%PROGRAMDATA%\migasfree-client\mtls\`                      |

### Scheduled Execution with systemd

On servers or headless machines (where `migasfree-play` does not run), continuous unattended convergence is typically set up using a systemd service and timer:

```ini
# /etc/systemd/system/migasfree-sync.timer
[Unit]
Description=Temporizador de sincronización periódica de migasfree
ConditionVirtualization=false

[Timer]
OnBootSec=5min
OnUnitActiveSec=2h
RandomizedDelaySec=10min
Persistent=true

[Install]
WantedBy=timers.target
```

Using `RandomizedDelaySec` is an essential architectural practice: it randomly disperses requests across a time window (e.g., 10 or 15 minutes), preventing thousands of machines starting up at the same hour from overloading production servers.

### Extension Points and Lifecycle Hooks

`migasfree-client` provides directories where administrators can place executable scripts to extend client behavior at three key synchronization moments:

* `/usr/share/migasfree-client/pre-sync.d/`: Scripts executed before connecting to the migasfree server.
* `/usr/share/migasfree-client/post-sync.d/`: Scripts executed after completing synchronization and package installation or removal.
* `/usr/share/migasfree-client/events.d/`: Reactive event handlers triggered only when a consolidated computer characteristic (*trait*) changes compared to the previous synchronization.

#### Structure and Variables in events.d

Upon detecting a characteristic change, the client generates two context files in `/usr/share/migasfree-client/events.d/` and searches for scripts in the subfolder matching the modified prefix:

```text
/usr/share/migasfree-client/events.d/
├── .env                     # Variables del estado actual y previo
├── .json                    # Diferencias en formato JSON (diff)
└── USR/                     # Subcarpeta para eventos del prefijo USR
    └── notify-profile.sh    # Script ejecutable
```

The `.env` file exposes two variables for each characteristic:

* `TRAIT_<PREFIX>`: Contains the current value assigned after synchronization (e.g., `TRAIT_USR="teacher"`).
* `BEFORE_TRAIT_<PREFIX>`: Stores the value it held before synchronization (e.g., `BEFORE_TRAIT_USR="alumn"`).

Reactive Bash script example (`events.d/USR/notify-profile.sh`):

```bash
#!/bin/bash
# Cargar las variables de entorno del evento
source /usr/share/migasfree-client/events.d/.env

# Reaccionar si el usuario asignado al puesto ha cambiado
if [ "$TRAIT_USR" != "$BEFORE_TRAIT_USR" ]; then
    logger -t migasfree-event "Usuario cambiado: $BEFORE_TRAIT_USR -> $TRAIT_USR"
    # Ejecutar acciones operativas locales (ej. notificar en el escritorio o recargar un demonio)
fi
```

#### NOTE
Scripts within these directories are executed in alphanumeric order. If a script in `pre-sync.d` exits with an error code, synchronization terminates immediately to preserve workstation integrity.

\

## migasfree-play

migasfree-play is the desktop graphical application that allows users to install software and devices from the catalog without needing superuser privileges.

### Integration and Environment Variables

migasfree-play requires no complex manual configuration: it automatically discovers the server and project via the local client (`migasfree.conf`). For testing or dev environments, it supports the following environment variables:

| Variable               | Purpose                                                                                            |
|------------------------|----------------------------------------------------------------------------------------------------|
| `MFP_USER`             | Technical user to authenticate against the catalog REST API.  *(Default: \`\`migasfree-play\`\`)*. |
| `MFP_PASSWORD`         | Technical user password for access.  *(Default: \`\`migasfree-play\`\`)*.                          |
| `MFP_EXECUTIONS_LIMIT` | Simultaneous operations limit in the graphical execution queue.  *(Default: \`\`5\`\`)*.           |
| `MFP_QUASAR_PORT`      | Quasar/Vite development server port.  *(Default: \`\`9999\`\`)*.                                   |
\

## migasfree-agent

`migasfree-agent` is the background service responsible for establishing secure TCP tunnels over WebSocket with the relay server, allowing remote assistance to computers behind firewalls or NAT without opening ports or needing a public IP.

### Zero Configuration and mTLS Reuse

True to the philosophy of operational simplicity, `migasfree-agent` **has no dedicated configuration file**:

1. **Auto-discovery**: Upon startup, it queries client configuration (via `migasfree conf` and `migasfree info`) to obtain the server, computer ID (CID), and project.
2. **mTLS certificate reuse**: Automatically uses certificates issued in `/var/migasfree-client/mtls/` (or `%PROGRAMDATA%\migasfree-client\mtls\` on Windows) to establish the encrypted and authenticated tunnel.
3. **Multiplexed services without inbound port forwarding**: Multiplexes local support services over the outbound secure tunnel: **SSH** (port 22), **VNC** (port 5900), and **RDP** (port 3389). Since it is an outbound connection initiated by the agent towards the server (HTTPS/WSS traffic), no incoming open ports or port forwarding rules are needed on the workstation firewall or router.

\

## Summary

With this chapter, we conclude **Part V** and with it the migasfree configuration reference:

* **migasfree-client** (`migasfree.conf` and `MIGASFREE_*` variables): server, project, upgrade policies, hardware inventory, environment variables, data paths, scheduled execution, and lifecycle hooks.
* **migasfree-play**: catalog credentials and environment variables for testing and development.
* **migasfree-agent**: zero-configuration model via CLI introspection, tunnel services (SSH, VNC, RDP), and mTLS certificate reuse.

With server infrastructure and workstation configuration finely tuned, you have complete knowledge to operate migasfree at scale with robustness and elegance.

It has been a long, intense journey through systems architecture, automation, and governance. This chapter concludes the main body of *Fun with migasfree*.

I want to sincerely thank you for your interest in the project and the effort dedicated to reading along.

And finally, will you join me in sharing a final reflection in the [Epilogue](epilogue.md#epilogo)?

# Epilogue

> Blessed is he who invented sleep, a cloak that covers all human thoughts.

If you’ve made it this far without skipping chapters just looking for the magic recipe to fix the third-floor printer, you have my utter respect and admiration.

But before you head back into the trenches, how about a coffee? I like to think we’re sitting face to face to share one final thought.

You probably know that familiar paradox of ours: the better you do your job, the more invisible you become. If everything boots up, printers don’t fail, and apps behave, there will always be someone thinking:  *“so what does the sysadmin actually do, if this runs by itself?”*.

In the same way, packaging suffers from this very same paradox. Relegated to “black magic”, we use it daily to install third-party software, but not to package our own configurations, thus missing out on a true engineering gem. We forget that the simple is not only beautiful: it works.

That very spirit drives migasfree: a project forged by sysadmins rebelling against the daily chaos that devours our working hours. The automation it offers gives us back what truly matters: time to think, experiment, be surprised, and, why not, *have fun*.

Open the console, set up your lab, tinker, craft your own recipes, break things (without wrecking production), lean on AI to package that configuration effortlessly, and release it.

It has been a pleasure sharing this experience and my little beatitudes with migasfree with you. And now excuse me, that cloak of sleep is beginning to cover me…

# VI. Annexes

This annex section compiles supplementary technical guides, transition procedures for legacy versions, advanced references, and auxiliary materials that support systems administrators in specific deployment and maintenance situations.

# Cookbook

This annex brings together a catalog of practical recipes to guide you through solving real-world scenarios, showing how to combine the various migasfree building blocks.

Although not an exhaustive catalog, these recipes provide the necessary mental and practical framework to approach systems management. To tackle them successfully, keep two key principles in mind:

* **Keep projects to a minimum**: Even though each recipe mentions a specific project, in real environments it is best to limit the number of projects to one per base distribution (such as Ubuntu 24.04 or Windows 11). Diversification by site, classroom, or department should be handled dynamically through **Attributes** and **Formulas**.
* **Follow a three-phase methodology**:
  1. **Client research**: First solve and validate the requirement on a test machine by identifying the affected commands and files.
  2. **Packaging**: Automate the solution by packaging it (as software or a formula) in the migasfree repository.
  3. **Deployment**: Design the server-side strategy by defining the targets (attributes and formulas) and execution schedule.

A final note: researching and packaging software takes time. Artificial Intelligence is an excellent ally to speed up both phases; take advantage of it without hesitation, while always ensuring full understanding and control over what you execute.

\

## Firefox ESR

* **Objective**: Ensure that all workstations have Firefox ESR configured with corporate bookmarks, telemetry disabled, and mandatory security extensions (such as uBlock Origin), without allowing the user to disable them.

  #### TIP
  You can copy and paste this objective directly into an AI agent: it will generate the appropriate `policies.json` file instantly. If anything fails or your Firefox version differs, describe the issue in the *prompt* and the AI will quickly adjust the structure.
* **Implementation with migasfree**:
  1. **Generating the policy file**: We create the browser’s `policies.json` file:
     ```json
     {
       "policies": {
         "DisableTelemetry": true,
         "DisableFirefoxStudies": true,
         "EnableTrackingProtection": {
           "Value": true,
           "Locked": true
         },
         "Bookmarks": [
           {
             "Title": "Portal del Empleado",
             "URL": "https://portal.acme.com",
             "Placement": "toolbar"
           }
         ],
         "ExtensionSettings": {
           "uBlock0@raymondhill.net": {
             "installation_mode": "force_installed",
             "install_url": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
           }
         }
       }
     }
     ```
  2. **Packaging**: Create the `acme-firefox-policy_1.0_all.deb` package including this file so it gets installed at `/usr/lib/firefox-esr/distribution/policies.json`. Rely on what you learned in [Chapter 7](chapter07.md#empaquetado), where we created the `acme-test-files` package (or ask an AI agent to use `acme-test-files` as a base to generate it for you, but always make sure to understand its inner workings).
  3. **Release and deployment**: Upload the package to the server (`migasfree upload`) and assign it to the base deployment for all computers (`SET-All Systems`). On the next synchronization, all browsers will apply the policy in a unified and immutable manner.

  #### NOTE
  Keeping the packaging project in a version control repository (GitLab, GitHub, etc.) does not just centralize code: it provides complete historical traceability, eases teamwork, allows reverting any change in seconds, and opens the door to integrating CI/CD pipelines to build and upload packages automatically to multiple migasfree projects in a single run.

\

## Printers

* **Objective**: Ensure that any computer (laptop or desktop) automatically installs the `PRN-555` laser printer upon connecting to network segment 

  ```
  ``
  ```

  192.168.3.0/27\*\*.
* **Implementation with migasfree**:
  1. **formula**: The default server formula `Network` serves our purpose. When a computer connected to this segment synchronizes, the server automatically assigns it the attribute `NET-192.168.3.0/27`. We do not need to do anything here.
  2. **Association**: In **Devices > Devices**, edit printer `PRN-555` and, under its **Logical devices** section, assign the **Attribute** `NET-192.168.3.0/27` to the desired capabilities (e.g., Black/White and Duplex).
  3. **Automatic convergence**: Upon booting any computer, the migasfree client synchronizes, detects membership in the network segment, and installs the printer with its drivers and CUPS queues instantly, without technical intervention. If the computer later connects to another segment, that printer will be magically uninstalled.

  #### NOTE
  We achieved the objective by associating only the essential elements (the printer with the network segment), without having to craft complex rules or manual scripts. With migasfree you focus on the what, not the how.

\

## Zero-Day

* **Objective**: Following the publication of a critical vulnerability with an active exploit (*Zero-Day*) in OpenSSH ([RegreSSHion](https://www.qualys.com/2024/07/01/cve-2024-6387/regresshion.txt) - CVE-2024-6387, affecting versions **8.5p1 to 9.7p1**), automatically detect vulnerable computers and apply the urgent mitigation (`LoginGraceTime 0` in `sshd_config`).

* **Implementation with migasfree**:
  1. **Packaging the mitigation**: As a temporary workaround while the distribution releases the patched version, we create the package `acme-cve-2024-6387_1.0_all.deb`. It simply includes the file `/etc/ssh/sshd_config.d/00-cve-2024-6397.conf` in the package. Its contents will be:
     ```text
     LoginGraceTime 0
     ```

     In the package’s post-installation script (`postinst`), we restart the `sshd` service so that the new configuration takes effect immediately.
  2. **Detection formula**: We add a formula that evaluates the `openssh-server` package version on the client and creates the attribute `CVE-2024-6387` if found within the affected range:
     ```python
     from migasfree_client.utils import get_package_version

     version = get_package_version("openssh-server")[0]
     if version:
                 match = re.search(r'(\d+\.\d+)p\d+', version)
                 if match and 8.5 <= float(match.group(1)) < 9.8:
                    print('2024-6387~Vulnerable a RegreSSHion')
                    exit()

     print("None")
     ```
  3. **Deployment**: We upload the package to the server and create a deployment configuring the following parameters:
     * **Name**: `CVE-2024-6387`
     * **Project**: The one corresponding to our environment.
     * **Included attributes**: `CVE-2024-6387` (this indicates who is affected).
     * **Source**: Internal
     * **Available packages**: `acme-cve-2024-6387_1.0_all.deb` (to release the package).
     * **Packages to install**: `acme-cve-2024-6387` (to enforce its installation).
  4. **Synchronization**: We trigger the synchronization command from the web management console to the entire fleet. Only vulnerable workstations will apply the vaccine and restart `sshd` in real time.
  5. **Disabling**: Once the base distribution publishes the new package with the vulnerability fixed, the **Deployment** and **Formula** can be disabled to prevent unnecessary resource usage on both clients and server.

  #### NOTE
  By combining version detection formulas with the attribute assignment engine, you avoid modifying immune machines while maintaining precise control and traceability.

\

## Hardware Inventory (SSD vs. HDD)

* **Objective**: Obtain accurate fleet information by identifying which computers have solid-state drives (SSD) and which still retain rotational mechanical drives (HDD) to plan hardware renewal campaigns.
* **Implementation with migasfree**:
  1. **Inspection formula**: In **Configuration > Formulas**, we create a **List Class** formula named `Store` with prefix `STR` that inspects the computer’s disks and returns detected components separated by commas:
     ```python
     import glob
     import os

     disks = set()
     for disk in glob.glob('/sys/block/sd*') + glob.glob('/sys/block/nvme*'):
         # Ignorar dispositivos virtuales o bucles
         if os.path.exists(f'{disk}/queue/rotational'):
             try:
                 with open(f'{disk}/queue/rotational') as f:
                     if f.read().strip() == '1':
                         disks.add('HDD~Disco Mecánico')
                     else:
                         disks.add('SSD~Disco Estado Sólido')
             except OSError:
                 pass

     print(' , '.join(sorted(disks)))
     ```
  2. **Automatic inventory**: On the next synchronization, migasfree will automatically assign the corresponding attributes to the computer (e.g., if a machine has an SSD for the system and a secondary HDD for data, it will receive both attributes simultaneously).
  3. **List export**: Getting the precise list of computers still holding mechanical drives is as simple as navigating to **Configuration > Attributes**, editing the attribute `STR-HDD`, accessing its **Related Computers**, and exporting the result to a CSV file to work with in a spreadsheet.
  4. **Completion and cleanup**: Once the SSD replacement campaign is completed, the **Formula** can be disabled on the server to prevent unnecessary resource consumption during client synchronizations.

  #### NOTE
  By configuring the formula as **List Class**, the migasfree backend splits the comma-separated string returned by the script and increments/assigns each attribute independently. This allows recording hybrid configurations (SSD + HDD) cleanly and declaratively, facilitating quick list exports for decision making.

  #### TIP
  **Alternative with Artificial Intelligence and MCP**: Since the hardware inventory already resides in the migasfree database, a quick alternative is to ask an AI agent equipped with the migasfree MCP server directly. The assistant will generate and execute the appropriate SQL query in real time, returning the list to you without needing to create formulas.

\

## Proactive Health Diagnostics

* **Objective**: Proactively detect computers experiencing degradation in physical storage (disk S.M.A.R.T. attributes) before the user suffers data loss or service disruption, automatically notifying technical support.
* **Implementation with migasfree**:
  1. **Diagnostic script**: In **Configuration > Fault definitions**, we create a new definition named `Storage Health`. In the code field, we enter a Python script that audits disk S.M.A.R.T. counters:
     ```python
     import subprocess

     # Comprobación de salud S.M.A.R.T. si la utilidad smartctl está disponible
     try:
         res = subprocess.run(
             ['smartctl', '-H', '/dev/nvme0'],
             capture_output=True,
             text=True
         )
         if 'FAILED!' in res.stdout:
             print(
                 "ALERTA CRÍTICA: El disco /dev/nvme0 reporta fallos S.M.A.R.T. inminentes. "
                 "Acción: Programar sustitución física de la unidad de inmediato."
             )
     except FileNotFoundError:
         pass
     ```
  2. **Recipients and scope configuration**: We constrain execution by adding the included attribute `PLT-Linux`. Optionally, we assign the fault to the user profile group `Computer Checker` so that alerts reach the support technicians’ dashboard.
  3. **Silent evaluation and automatic alerting**: On each periodic synchronization, the client runs the test transparently:
     * If everything works correctly (exit code 0 and empty output), no alert is generated.
     * If an anomaly is detected, the script’s printed output is transmitted to the server, where it is logged under **Data > Faults** and increments the web console alert counter in real time.

  #### NOTE
  Unlike formulas (which classify computers by assigning them attributes), **Fault definitions** are designed to notify anomalies proactively. If the test passes, they generate no noise; if it fails, they immediately alert technicians indicating the root cause and suggested corrective action.

# REST API

> > Automation is not just about doing things faster, but about making them reliable, repeatable, and scalable.

The REST API exposed by the `core` service constitutes migasfree’s most powerful programmatic interface. Through it, you can query inventory status, manage deployment policies, assign attributes, and automate any integration with third-party corporate systems (such as ticketing tools, CMDBs, or monitoring systems).

This annex describes authentication mechanisms, the structure of requests and responses, and complete practical examples in Bash (using `curl` and `jq`) and Python.

## Token-Based Authentication

To consume the API securely from external scripts or applications, migasfree uses user *token* authentication. Each request must include the `Authorization` HTTP header in the format:

> ```text
> Authorization: Token <tu_token_secreto>
> ```

### Obtaining the Access Token

There are two ways to obtain an API token:

1. **From the web management console**: By accessing your user profile in the web interface (`console`) and viewing or generating the API key (*API Token*).
2. **Via an HTTP request to the authentication endpoint**:
   ```bash
   curl -X POST https://<FQDN>/token-auth/ \
     -H "Content-Type: application/json" \
     -d '{"username": "tu_usuario", "password": "tu_password"}'
   ```

   The response will return a JSON object containing the access token:
   ```json
   {
     "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
   }
   ```

## Interactive Exploration with Swagger / OpenAPI

The migasfree server incorporates an interactive documentation interface based on OpenAPI (Swagger). To explore it, open in your browser:

> `https://<FQDN>/status` and click on the **core** option.

This interactive interface is an indispensable tool for development and programming integrations. Through it, developers can:

* **Perform live tests**: Execute real HTTP requests directly against the server from the browser to understand the JSON response structure.
* **Inspect data schemas**: Learn field data types, mandatory fields, and expected formats.
* **Debug status codes**: Become familiar with success responses (200, 201) and common errors (400 Bad Request, 401/403 Auth, 404 Not Found).
* **Copy payloads**: Obtain ready-to-use JSON templates for `POST` or `PUT` requests in external scripts.

### MCP Server

To maximize developer productivity, migasfree integrates an MCP (*Model Context Protocol*) server. This service exposes API documentation and database schemas directly to Artificial Intelligence agents.

This allows your AI development environment to dynamically query endpoints, resolve doubts about available filters, or inspect table fields in real time, generating more precise integration code and drastically reducing debugging time. For more configuration details, see [AI Integration](annex03-mcp-integration.md#anexo-mcp).

## API Structure and Conventions

* **Format**: All responses and payloads are exchanged in JSON format (`Content-Type: application/json`).
* **Pagination**: Resource lists accept the `limit` and `offset` query parameters to paginate large volumes of data:
  ```text
  https://<FQDN>/api/v1/token/computers/?limit=50&offset=100
  ```
* **Search and filtering**: Most endpoints support text searches via the `search` parameter (e.g., `?search=laptop-ventas`) and direct field filters (e.g., `?project=ACME-1` or `?status=synced`).

## Main Resources

The most commonly used endpoints for automated administration are:

* **\`\`/api/v1/token/computers/\`\`**: Query and manage computer inventory (hostname, IP, hardware, last synchronization timestamp, assigned attributes, etc.).
* **\`\`/api/v1/token/attributes/\`\`**: Creation and query of attributes (tags, logical formulas, and membership criteria).
* **\`\`/api/v1/token/deployments/\`\`**: Definition of package deployment policies and computer assignment rules.
* **\`\`/api/v1/token/packages/\`\`**: Catalog of software packages available in repositories.
* **\`\`/api/v1/token/projects/\`\`**: Projects and distributions managed by the server.

## Practical Examples

### Example 1: Querying Computers via Bash and curl

The following Bash script queries the list of registered computers and extracts their name, status, and last synchronization date by processing the JSON output with `jq`:

> ```bash
> #!/usr/bin/env bash
> set -euo pipefail

> FQDN="migasfree.acme.com"
> TOKEN="9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

> curl -s -k \
>   -H "Authorization: Token ${TOKEN}" \
>   -H "Content-Type: application/json" \
>   "https://${FQDN}/api/v1/token/computers/?limit=20" \
>   | jq -r '.results[] | "\(.id)\t\(.name)\t\(.status)\t\(.sync_end_date)"'
> ```

You will get output similar to this:

> ```text
> 1   debian13        assigned        2026-08-24T12:57:02.792475+02:00
> 2   mci-builder     assigned        2026-08-21T10:30:19.336690+02:00
> ```

### Example 2: Automation in Python

The following Python script uses the `requests` library to query computers and display an inventory summary (including status):

> ```python
> import os
> import requests

> FQDN = "migasfree.acme.com"
> TOKEN = os.getenv("MIGASFREE_API_TOKEN", "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b")
> BASE_URL = f"https://{FQDN}/api/v1/token"

> headers = {
>     "Authorization": f"Token {TOKEN}",
>     "Content-Type": "application/json",
> }

> response = requests.get(f"{BASE_URL}/computers/", headers=headers, verify=False)
> response.raise_for_status()

> data = response.json()
> computers = data.get("results", [])

> print(f"Total computers retrieved: {len(computers)}")
> for pc in computers:
>     print(f"- ID: {pc.get('id')} | Name: {pc.get('name')} | Status: {pc.get('status')}")
> ```

You will get output similar to this:

> ```text
> Total computers retrieved: 2
> - ID: 1 | Name: debian13 | Status: assigned
> - ID: 2 | Name: mci-builder | Status: assigned
> ```

# AI Integration

> Artificial intelligence is the new electricity.

In [Chapter 10 (Stack)](chapter10.md#stack) we introduced the `mcp-server` service, the platform component that implements the open [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) standard. Through it, artificial intelligence assistants (such as Antigravity, Claude Desktop, or Cursor) can query the fleet securely and in natural language. This annex details the capabilities exposed by the server, the steps to connect an assistant, and a collection of practical, ready-to-use queries.

## MCP Server Capabilities

The MCP server exposes three fundamental protocol primitives: **tools**, **resources**, and **instruction templates** (*prompts*).

### Tools

Tools allow the AI agent to perform dynamic queries against the infrastructure:

* **db_query**: Executes arbitrary SQL `SELECT` queries directly against the migasfree PostgreSQL database. The server strictly validates that the statement is read-only and enforces the restrictions of the `mcp_ro` role.
* **read_doc**: Compatibility tool for clients that do not support direct reading of MCP resources. Allows querying or listing server technical documents (such as database schemas, architecture, or API specifications).

### Resources

Resources provide live documentation and continuous technical context to language models via URI schemes (`<STACK>://docs/...`):

* **documentation_index.md**: Master index of available technical documentation.
* **db_schema.md**: Complete relational structure of the database (tables, columns, data types, and foreign keys).
* **migasfree-user-manual.md**: Official user manual converted to Markdown.
* **migasfree_architecture.md**: Technical description of service architecture and data flow.
* **github_repositories.md**: Catalog of all official repositories in the migasfree ecosystem.
* **api_core.md** and **api_manager.md**: OpenAPI specifications for server REST interfaces.
* **faq.md**: Troubleshooting guide and frequently asked questions about the platform.

### Instruction Templates (*Prompts*)

The server includes predefined templates that guide the assistant through common management tasks:

* **analyze_fleet**: Performs a comprehensive fleet analysis (distribution by status, assigned projects, recent activity, and unsynchronized computers).
* **find_sync_errors**: Diagnoses errors and disruptions in workstation synchronizations.
* **query_builder**: Assists in crafting accurate SQL queries from natural language questions.

## Configuring in Antigravity

Integrating the MCP server with Antigravity takes three steps:

1. **Enable network access in migasfree**: For security reasons, MCP server access is restricted to local connections (`127.0.0.1`) by default. To authorize connections from the machine running Antigravity, edit `stack.conf` by defining the allowed IP or CIDR range:
   ```python
   NETWORK_MCP = '192.168.1.50'  # O un rango CIDR como '192.168.1.0/24'
   ```

   Apply the changes to the cluster with:
   ```bash
   migasfree-swarm deploy
   ```
2. **Install the CA certificate (if using custom certificates)**: If the server uses a private CA rather than a public Let’s Encrypt certificate, install the CA on the host machine running Antigravity:
   ```bash
   sudo wget --no-check-certificate -O /usr/local/share/ca-certificates/ca-<FQDN>.crt https://<FQDN>/pool/install/ca-<FQDN>.crt
   sudo update-ca-certificates --fresh
   ```

   #### NOTE
   Since Node.js and Electron-based environments do not consult the OS system certificate store by default, you need to point Node.js to the certificate path using the `NODE_EXTRA_CA_CERTS` environment variable (e.g., in `~/.bashrc`):
   ```bash
   export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
   ```

   Alternatively, in lab environments or local testbeds without public domains, you can connect directly over unencrypted HTTP (`http://<FQDN>/mcp/sse`).
3. **Register the server in Antigravity**: The migasfree MCP server uses **SSE** (*Server-Sent Events*) transport. Add the server configuration to the MCP configuration file (globally in `~/.gemini/antigravity-ide/mcp_config.json` or at project level in `.agents/mcp_config.json`):
   ```json
   {
     "mcpServers": {
       "migasfree": {
         "serverUrl": "http://<FQDN>/mcp/sse"
       }
     }
   }
   ```

Once connected, Antigravity will automatically have access to all server tools, resources, and documentation to query the fleet status in real time.

## Use Cases and Natural Language Queries

Once the MCP server is connected, the AI assistant acts as a genuine analyst and expert co-pilot over the migasfree infrastructure. You can ask direct natural language questions without needing knowledge of SQL syntax, REST API calls, or internal database table schemas.

The language model queries context resources (such as `db_schema.md` or technical documentation), formulates the necessary read-only queries, executes them using `db_query`, and synthesizes answers into reports, tables, or actionable explanations.

Practical examples of what you can request span multiple operational domains:

* **Hardware audit and inventory**:
  * Show a list of computers with less than 16 GB of RAM.
  * What are the most common processor manufacturers and models in our computer fleet?
  * Identify computers that have more than one active network interface.
* **Software and deployment control**:
  * Which computers have the `nano` package installed and what version do they have?
* **Operational health and synchronization monitoring**:
  * Which computers haven’t synchronized with the server in over 30 days?
  * Analyze synchronization errors and failures recorded in the last 24 hours and summarize the main root causes.
  * Are there computers that started a synchronization but failed to finish it properly?
* **Segmentation, tags, and statistics**:
  * Generate a table showing the distribution of computers grouped by operating system, version, and architecture.
  * How many computers have the `FLV-LXDE` attribute assigned?
* **Documentation queries**:
  * Explain how migasfree works for a newcomer.
  * What does “fun with migasfree” say regarding a “fried egg”?
* **API queries**:
  * Which endpoint should I use to list projects, and what parameters does it accept?
  * Show an example using `curl` to authenticate via JWT token and query registered computers.
  * How is the JSON payload structured to create a new deployment via the API?
* **PostgreSQL database schema queries**:
  * Which tables store synchronization info and which foreign keys relate them to computers?
  * Describe the columns and data types of the computers table.
  * Which tables are related to hardware inventory?

With these capabilities, the assistant becomes a co-pilot capable of auditing the fleet, explaining the platform, and drafting diagnostics on the fly. To see how this server is used in operational incident troubleshooting, see [Chapter 22 (Observability)](chapter22.md#observabilidad-monitorizacion-y-resolucion-de-incidencias).

# CLI Reference

> > Make each program do one thing and do it well.

Throughout the book, migasfree command-line tools are repeatedly invoked. This annex brings together the main subcommands and options of each utility into a single reference point, so you can resolve any doubts without having to reopen the chapter where they were introduced.

\

## migasfree-client

The `migasfree` client is the workstation convergence tool. It combines a catalog of dedicated subcommands for each task with the global debugging mode `--debug` (see [Chapter 16 (Client Environment)](chapter16.md#entorno-cliente)):

| Command                                                     | Description                                                                                     |
|-------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `migasfree --help`                                          | Displays general help and available subcommands.                                                |
| `migasfree sync`                                            | Executes standard synchronization with the server (convergence cycle).                          |
| `migasfree sync --force-upgrade`                            | Forces package upgrades ignoring the `Auto_Update_Packages` setting.                            |
| `migasfree sync --hardware`                                 | Selectively synchronizes the hardware inventory subsystem.                                      |
| `migasfree sync --devices`                                  | Selectively synchronizes the device subsystem.                                                  |
| `migasfree info` / `migasfree info -j`                      | Queries computer info registered on the server (in JSON with `-j`).                             |
| `migasfree attributes`                                      | Queries assigned attributes and computer CID identifier (`-j` or `--cid`).                      |
| `migasfree tags --get` / `--set <tag>`                      | Queries or assigns tags to the computer from the command line.                                  |
| `migasfree label`                                           | Displays the computer ID label on screen (helpdesk support).                                    |
| `migasfree search <pattern>`                                | Searches available packages in assigned stores.                                                 |
| `migasfree install <package>` / `migasfree purge <package>` | Installs or uninstalls packages abstracting away the local [PMS](annex05-glossary.md#term-PMS). |
| `migasfree conf`                                            | Queries or modifies local configuration (`/etc/migasfree.conf`) with `--json`.                  |
| `migasfree import-mtls <file>`                              | Manually imports packaged mTLS certificates.                                                    |
| `migasfree upload -f <package> -j <project> -s <store>`     | Uploads a package to the server store from a packaging workstation.                             |
\

## migasfree-swarm

`migasfree-swarm` centralizes the Docker Swarm cluster lifecycle: stack deployment, security, topology, and backup (see [Chapter 9 (Infrastructure)](chapter09.md#infraestructura)):

| Command                                            | Description                                                                          |
|----------------------------------------------------|--------------------------------------------------------------------------------------|
| `migasfree-swarm config`                           | Generates initial cluster configuration (`cluster.conf`).                            |
| `migasfree-swarm deploy` / `undeploy` / `redeploy` | Deploys, tears down, or reinstalls a service stack (`-all` suffix for all).          |
| `migasfree-swarm pull`                             | Pulls all service images.                                                            |
| `migasfree-swarm consoles-dev` / `consoles-pro`    | Enables or disables development consoles (Portainer, Flower, pgAdmin, RedisInsight). |
| `migasfree-swarm secret`                           | Displays console access credentials.                                                 |
| `migasfree-swarm url-admin-certificate`            | Generates a one-time URL to issue the administration certificate.                    |
| `migasfree-swarm join-worker` / `leave`            | Adds a worker node to the cluster or leaves the current node.                        |
| `migasfree-swarm backup` / `restore`               | Performs or restores PostgreSQL and Redis dumps.                                     |
| `migasfree-swarm prune`                            | Removes dangling images from the node.                                               |
| `migasfree-swarm info`                             | Displays cluster and stack information.                                              |

## Packaging and Publishing Packages

Uploading packages to the server is done from an authorized packaging workstation via `migasfree upload` (or its binary `migasfree-upload`), specifying the file, project, and target store (see [Chapter 7 (Packaging)](chapter07.md#empaquetado)):

> ```bash
> migasfree upload -f mi-paquete_1.0_all.deb -j Proyecto-Base -s almacén
> ```
\

## migasfree-agent and migasfree-play

* **migasfree-agent**: servicio residente que abre túneles WebSocket inversos basados en mTLS para
  el acceso remoto (SSH, VNC, RDP). No dispone de órdenes directas; su ejecución remota queda
  restringida por la lista blanca `ALLOWED_COMMANDS` (ver [Capítulo 24 (Cliente)](chapter24.md#cliente)).
* **migasfree-play**: aplicación gráfica de autoservicio (Electron, Vue y Quasar) configurada por
  variables de entorno; no se administra por línea de órdenes (ver [Capítulo 16 (Entorno
  Cliente)](chapter16.md#entorno-cliente)).

# Glossary

Alert
: Visual notice or notification log generated by the migasfree server for the administrator to give priority attention to a relevant event, technical fault, or operational drift on one or more fleet computers.

APK
: Alpine Package Keeper. Native, lightweight, and high-performance package manager used in Alpine Linux and in the MCS cloning system.

App Paths
: Microsoft Windows registry key where the WPT manager registers the primary application executables to allow clean invocation without polluting the PATH.

APT
: Advanced Package Tool. Standard high-level package manager in Debian and Ubuntu-based GNU/Linux distributions that resolves dependencies and interacts with deb repositories.

Apt-cacher-ng
: Specialized HTTP software package caching proxy server deployed in remote branch offices to drastically reduce WAN bandwidth consumption.

Attribute
: Concrete, evaluated, and typed value acquired by a formula after execution and introspection on a specific client computer during the synchronization cycle.

Attribute Set
: Declarative, reusable structure grouping multiple attributes with topological resolution, allowing complex operational profiles to be modeled while preventing circular dependencies.

Audit
: Systematic inspection, traceability, and continuous evaluation procedure regarding software changes, hardware status, and configurations applied across the fleet.

Auto-failover
: Automatic failover mechanism where a replica node immediately and transparently takes over the master node functions upon an unexpected failure.

AZLinux
: Corporate GNU/Linux distribution of the Zaragoza City Council based on Debian/Ubuntu and entirely managed with migasfree to support municipal workstations.

Base Deployment
: Highest-priority permanent deployment designed to establish the core, immutable operating system configuration across all linked machines.

Baseline
: Formal specification (*baseline*) or agreed set of SCI versions serving as a stable, frozen starting point for subsequent development or changes.

Bootstrap
: Initialization and autonomous initial installation process whereby the base management tool (such as `windows-package-tool`) is deployed onto a clean system to enable it to download and configure the rest of the suite.

CA
: Certificate Authority. Internal migasfree cryptographic entity responsible for issuing, signing, and revoking X.509 certificates for machines and services.

CCS
: Change Control System. Set of procedures and tools responsible for tracking, governing, validating, and auditing modifications made to systems and packages over time.

Celery
: Asynchronous task queue framework based on message passing used by migasfree to delegate heavy processing and concurrent synchronization to background workers.

Change
: Planned technical activity that modifies a Software Configuration Item (SCI), generating a new identifiable and traceable version within the change control system.

CID
: Computer Identifier. Unique, sequential, and immutable integer assigned by the server to a computer’s motherboard upon self-registration.

Closed-Loop Control
: Governance principle (*closed-loop governance*) according to which the actual state of client workstations is continuously and automatically inspected, reported, and remediated against the target state defined in server policies.

Command Whitelist
: Security directive (ALLOWED_COMMANDS) in `migasfree-agent` restricting remote executions exclusively to a closed, secure set of authorized binaries.

Computer Replacement
: Procedure whereby a new machine inherits the CID, attributes, history, and deployments of a replaced computer.

Computer Status
: Operational status assigned to a machine in the inventory (Assigned, Reserved, Unknown, In Repair, Available, or Decommissioned) governing its synchronization.

Configuration Package
: Software package (*config package*) specifically intended not to compile binaries, but to apply and version configuration directives, themes, or file diverts.

Convergence Cycle
: Sequential flow structured in phases (mTLS, introspection, directives, PMS execution, logical devices, and telemetry) executed by `migasfree-client` during each synchronization to align the workstation state with the server.

Core
: Central migasfree server microservice (built with Django) managing the data model, business logic, web administration console, and primary REST API.

CUPS
: Common UNIX Printing System. Standard modular print system and server for UNIX and Linux managed by migasfree to automatically deploy and configure print queues.

Datashares
: Shared storage volumes (local or NFS) where packages, software repositories, machine certificates, and server public keys are stored.

dd
: Classic UNIX utility for low-level block-by-block data copying and conversion, used in the MCS cloning engine.

Declarative Convergence
: Mechanism by which the migasfree client computes discrepancies between the computer’s current state and server directives, executing necessary package manager transactions to reach the target state without manual intervention.

Deployment
: Declarative directive associating a set of packages from a store with a target group of computers, conditioned by attributes, singularities, or tags.

Deployment Level
: Package assignment mode in a deployment determining whether installation is mandatory (Admin Level) or on-demand (User Level in migasfree-play).

Deployment Priority
: Numerical conflict-resolution criterion determining which deployment takes precedence when conflicting directives exist for the same package on a given computer.

Deployment Rollout Delay
: Time dispersion mechanism distributing the actual rollout of a deployment over a span of days, avoiding traffic spikes and WAN saturation.

Deployment Schedule
: Time rule establishing the start date, expiration date, and progressive rollout delay in days for the distributed application of a deployment.

Device Model
: Technical spec sheet in migasfree defining a specific peripheral along with its PPD drivers and supported configuration options.

Device Replacement
: Administrative action replacing a physical device with another, automatically inheriting its previous assignment and settings.

Disaster Recovery
: Planned set of technical procedures and policies aimed at restoring migasfree infrastructure, data, and service operations following a major disaster.

Domain
: Logical partition of the migasfree database isolating computer management and visibility according to delegated organizational or departmental scopes.

EFI Partition
: FAT32-formatted disk partition containing bootloader binaries for motherboards with UEFI architecture.

Error
: Syntax error, technical failure, or runtime exception detected during communication or package manager transactions on the client.

Fault
: Anomalous condition, functional issue, or system degradation actively detected on the client after evaluating a *Fault definition* directive.

File Diverts
: Packaging mechanism (*diverts*) allowing a corporate package to override an original OS configuration file without conflicting with the upstream maintainer’s package.

FileBrowser
: Web tool integrated into the operational consoles to visually browse, inspect, and manage files in migasfree shared storage.

Flower
: Real-time web monitoring console for Celery clusters allowing supervision of asynchronous task statuses, active workers, and execution rates.

Formula
: Executable code (Python or shell script) evaluated on the client workstation to inspect and return a specific hardware, software, or user attribute.

FQDN
: Fully Qualified Domain Name. Canonical, DNS-resolvable hostname of the migasfree server, essential for mTLS certificate validation.

GPG
: GNU Privacy Guard. Encryption and digital signature tool used by migasfree to cryptographically sign package repository metadata.

HAProxy
: High-performance load balancer and reverse proxy centralizing inbound traffic, SSL/TLS termination, and routing to stack microservices.

HOME Partition
: Dedicated disk partition (HOME.raw) storing users’ personal data and configurations decoupled from the operating system.

Idempotence
: Fundamental property whereby repeated execution of a configuration operation produces exactly the same system result without cumulative side effects.

JWT
: JSON Web Token. Compact open standard used by migasfree for secure user and process authentication and authorization across the REST API.

Local Attribute
: Attribute calculated and stored locally in the client workstation database, used to optimize decision making without requiring continuous network queries.

Logical Device
: Abstract representation in migasfree of a physical peripheral (such as printers or scanners), decoupled from the specific computer it is connected to.

lshw
: Command-line utility for GNU/Linux generating a detailed hierarchical report on the computer’s physical components and hardware configuration.

lshw-windows-emulator
: Tool emulating the standard JSON output of `lshw` on Microsoft Windows systems, translating WMI/CIM hardware classes to enable homogeneous inventorying.

Machine Certificate
: X.509 cryptographic file (client.crt and client.key) securely and unambiguously binding a client workstation’s identity to the server’s corporate CA.

Manager
: High-performance microservice built with FastAPI responsible for reactive synchronization management, concurrency control, and remote tunnel orchestration.

Manufacturer
: Administrative entity cataloging supported commercial hardware and peripheral brands.

MCP
: Model Context Protocol. Interoperability protocol enabling AI models and agents to interact securely with migasfree data and APIs.

MCS
: Migasfree Clone System. Lightweight deployment OS based on Alpine Linux designed for master disk image cloning over network (HTTP streaming) or USB drive.

Metadata
: Structured data describing contents, dependencies, version, compatible architectures, and control directives of a package or software item.

MGI
: Migasfree Golden Image. Standardized, reproducible, and declarative golden master system image packaged as a base artifact for unattended cloning with MCS.

migasfree-agent
: Continuous background service establishing secure, mTLS-based reverse WebSocket tunnels with the server, enabling interactive remote support (SSH, VNC, RDP, web terminal).

migasfree-client
: Workstation synchronization engine responsible for negotiating secure mTLS channels, discovering inventory, evaluating directives, and converging state via the package manager.

migasfree-play
: Desktop graphical application (Electron, Vue, and Quasar) providing a corporate self-service app store where users install approved software.

migasfree-swarm
: Command-line orchestration tool to deploy, scale, back up, and manage the migasfree microservice cluster on Docker Swarm.

mTLS
: Mutual Transport Layer Security (*Mutual TLS*). Cryptographic protocol where both client and server authenticate each other using X.509 certificates.

NFS
: Network File System. Distributed file system protocol used in multi-node deployments to share data volumes among all swarm cluster nodes.

NSSM
: Non-Sucking Service Manager. Windows service wrapper used to run `migasfree-agent` as a native, resilient operating system service.

OpenAPI
: Standard, interactive specification for documenting and describing RESTful APIs (Swagger), accessible interactively at the server’s /docs path.

Operational Consoles
: Unified dashboard accessible at /status bringing together diagnostic tools, real-time metrics, and stack administration (Portainer, Flower, pgAdmin, RedisInsight).

Orphan Package
: Package hosted in a server store that is not linked to any active deployment.

Overlay
: Customization and script layer merged on top of the base system during MCS ISO image creation.

Package
: Standardized archive file (such as .deb, .rpm, .apk, or .wpt) encapsulating files, control scripts, and metadata ready for package manager processing.

Package Set
: Logical and versioned grouping of one or more packages within a store, designed to be assigned as a coherent atomic unit to software deployments.

Packaging Workstation
: Authorized workstation equipped with certificates and signing keys to upload packages to the server via the `migasfree upload` command.

Permanent Deployment
: Continuous deployment without an expiration date, ensuring assigned software and configurations remain active indefinitely across the fleet.

pgAdmin
: Web-based graphical administration and analytics environment for PostgreSQL database servers, integrated into development operational consoles.

Pgpool-II
: PostgreSQL middleware acting as a read query load balancer, connection pooling manager, and automatic failover switch.

Platform
: Definition of client operating system distribution and architecture (Debian, Ubuntu, Red Hat, Alpine, Windows) managed by a project.

PMS
: Package Management System. Native OS program (APT, DNF, Pacman, APK, WPT) responsible for resolving dependencies and installing software.

Portainer
: Container management web UI integrated into migasfree operational consoles to monitor resources and inspect live logs.

PostgreSQL
: Advanced transactional relational database management system used by migasfree as its primary structured data storage engine.

PPD
: PostScript Printer Description. Text file describing the capabilities, fonts, and advanced configuration options of a CUPS printer driver.

Project
: Primary organizational entity in migasfree defining the base OS, package stores, encryption keys, and directives for a fleet of workstations.

Python-Shell
: Node.js bridge module used in `migasfree-play` to safely run Python calls and commands from the Electron backend.

QEMU
: Hardware machine emulator and virtualizer used to test and validate golden master images and MCS cloning processes in dev environments.

RDP
: Remote Desktop Protocol. Microsoft remote desktop protocol natively supported through secure `migasfree-agent` tunnels on Windows workstations.

Redis
: In-memory data structure store used in the stack as a transactional caching datastore and messaging queue for Celery workers.

RedisInsight
: Interactive visual console for inspecting, memory analysis, and monitoring keys and queues in Redis.

Release
: Formal action of promoting and placing a specific package version into a software store, making it available for distribution via deployments.

REST API
: Application Programming Interface based on HTTP and REST principles, exposing migasfree resources and operations in JSON format for external integrations and automation.

Reverse Tunnel
: Secure communication channel initiated from the client towards port 443 of the server, allowing administrators remote access to the computer without opening local inbound ports.

Rolling Update
: Zero-downtime rolling update strategy where service replicas are replaced progressively without interrupting platform availability.

RPM
: RPM Package Manager. Standard package format and management system across the Red Hat distribution family (RHEL, Fedora, Rocky Linux).

RPO
: Recovery Point Objective. Metric of the maximum tolerable amount of data loss expressed in elapsed time since the last backup.

RTO
: Recovery Time Objective. Maximum allowable duration to restore full service operations following an outage.

SCI
: Software Configuration Item. Software entity (source code, configuration file, binary, or documentation) subject to SCM control, versioning, and tracking disciplines.

SCM
: Software Configuration Management (SCM). Software engineering discipline identifying, controlling, maintaining integrity, and auditing changes in computer systems throughout their lifecycle.

Scope
: Subset of computers defined within a domain to limit visibility, filtering, and delegated administration scope to specific operators.

Singularity
: Combined logical expression or boolean formula enabling surgical segmentation and identification of computer groups.

SMS
: Systems Management System. Comprehensive solution for managing, inventorying, configuring, and delivering software across computer fleets.

Store
: Centralized storage space and repository on the server hosting software packages and their control files (metadata) associated with a project, organized according to their release status.

Swarm
: Docker’s native clustering orchestration mode used by migasfree to coordinate high availability, load balancing, and microservice isolation.

System Formula
: Predefined formula built into the migasfree core to introspect universal hardware and operating system properties.

SYSTEM Partition
: Primary disk partition (SYSTEM.raw) hosting the OS root filesystem and applications in the MCS image structure.

Systemd Timer
: Native system timer used in Linux to schedule automatic `migasfree-client` synchronizations with randomized dispersion (*RandomizedDelaySec*).

Tag
: Administrative label (*tag*) assigned manually or automatically to a computer to classify it or dynamically condition deployment application.

Tag Category
: Taxonomic grouping used to classify and organize administrative tags (e.g., Sites, Departments, Classrooms, or User Profiles).

Telemetry
: Set of performance metrics, usage statistics, status logs, and historical data gathered from each client during each sync session.

Temporary Deployment
: Deployment subject to a temporal schedule that automatically expires upon reaching its deadline, ideal for transient migration campaigns or one-off installations.

TLS/SSL Certificate
: Digital server certificate enabling HTTPS communication encryption and authenticating the web server’s FQDN to browsers and clients.

Transactional Backup
: Consistent backup that preserves the exact state of relational databases (PostgreSQL) and in-memory structures (Redis) at a given point in time.

Triad
: Coordinated suite of the three migasfree client components (`migasfree-client`, `migasfree-agent`, and `migasfree-play`), covering configuration convergence, secure remote access, and the user self-service catalog, respectively.

Tunnel Multiplexing
: Technique used by `migasfree-agent` to carry multiple independent communication channels (control channels, SSH terminals, VNC or RDP sessions) over a single persistent WebSocket connection.

Turbo Clone
: High-speed cloning technique in MCS based on direct network streaming of raw disk images through pipeline streams (`wget | dd`).

User Formula
: Custom formula created by administrators to collect data or characteristics specific to the corporate or business environment.

User Profile
: Set of permissions and role restrictions assigned to a user account within the migasfree web management console.

UUID
: Universally Unique Identifier. 128-bit alphanumeric string used to unambiguously identify a client machine’s motherboard.

Virtualenv
: Isolated Python virtual environment (`venv`) encapsulating dependencies and interpreters independently of the host operating system.

Vitalinux
: Educational operating system of the Autonomous Community of Aragon based on Ubuntu and centrally governed via migasfree to support educational centers.

Wheel
: Standard binary packaging format for Python libraries (`.whl`), used by WPT to deploy dependencies in isolated virtual environments without compiling on the client machine.

WMI
: Windows Management Instrumentation. Microsoft Windows COM-based management and instrumentation infrastructure allowing inspection of hardware, devices, and OS state, used by `lshw-windows-emulator`.

WPT
: Windows Package Tool. Modular package manager for Microsoft Windows implementing isolated Python virtual environments (`venv`) and `App Paths` registry entries.
