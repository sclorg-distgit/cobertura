%global pkg_name cobertura
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

Name:           %{?scl_prefix}%{pkg_name}
Version:        1.9.4.1
Release:        9.14%{?dist}
Summary:        Java tool that calculates the percentage of code accessed by tests

# ASL 2.0: src/net/sourceforge/cobertura/webapp/web.xml
# GPL+: src/net/sourceforge/cobertura/reporting/html/files/sortabletable.js
#       src/net/sourceforge/cobertura/reporting/html/files/stringbuilder.js
# MPL 1.1, GPLv2+, LGPLv2+: some files in src/net/sourceforge/cobertura/javancss/ccl/
# rest is mix of GPLv2+ and ASL 1.1
License:        ASL 1.1 and GPLv2+ and MPL and ASL 2.0 and GPL+
URL:            http://cobertura.sourceforge.net/

# ./create-tarball.sh %%{version}
Source0:        %{pkg_name}-%{version}-clean.tar.gz
# POMs based from those available from the Maven repository
Source1:        http://repo1.maven.org/maven2/net/sourceforge/%{pkg_name}/%{pkg_name}/%{version}/%{pkg_name}-%{version}.pom
Source2:        http://repo1.maven.org/maven2/net/sourceforge/%{pkg_name}/%{pkg_name}-runtime/%{version}/%{pkg_name}-runtime-%{version}.pom
Source3:        http://www.apache.org/licenses/LICENSE-1.1.txt
Source4:        http://www.apache.org/licenses/LICENSE-2.0.txt
Source5:        create-tarball.sh

Patch0:         %{pkg_name}-unmappable-characters.patch

BuildRequires:  %{?scl_prefix_java_common}ant
BuildRequires:  %{?scl_prefix_java_common}ant-junit
BuildRequires:  %{?scl_prefix_java_common}antlr-tool
BuildRequires:  %{?scl_prefix_java_common}apache-commons-cli
BuildRequires:  %{?scl_prefix_java_common}jakarta-oro
BuildRequires:  %{?scl_prefix_java_common}jaxen
BuildRequires:  %{?scl_prefix_java_common}jdom
BuildRequires:  %{?scl_prefix_java_common}junit
BuildRequires:  %{?scl_prefix_java_common}log4j
BuildRequires:  %{?scl_prefix_java_common}objectweb-asm
BuildRequires:  %{?scl_prefix_java_common}tomcat-servlet-3.0-api
BuildRequires:  %{?scl_prefix_java_common}xalan-j2
BuildRequires:  %{?scl_prefix_java_common}xerces-j2
BuildRequires:  %{?scl_prefix_java_common}xml-commons-apis
BuildRequires:  maven30-groovy

Requires:       %{?scl_prefix_java_common}ant
Requires:       %{?scl_prefix_java_common}jakarta-oro
Requires:       %{?scl_prefix_java_common}junit
Requires:       %{?scl_prefix_java_common}log4j
Requires:       %{?scl_prefix_java_common}objectweb-asm

BuildArch:      noarch

%description
Cobertura is a free Java tool that calculates the percentage of code
accessed by tests. It can be used to identify which parts of your
Java program are lacking test coverage.

%package        javadoc
Summary:        Javadoc for %{pkg_name}

%description    javadoc
This package contains the API documentation for %{pkg_name}.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable maven30 %{scl} - <<"EOF"}
set -e -x
%patch0 -p1

cp %{SOURCE3} LICENSE-ASL-1.1
cp %{SOURCE4} LICENSE-ASL-2.0

sed -i 's/\r//' ChangeLog COPYING COPYRIGHT README
%{?scl:EOF}

%build
%{?scl:scl enable maven30 %{scl} - <<"EOF"}
set -e -x
pushd lib
  ln -s $(build-classpath jaxen) .
  ln -s $(build-classpath jdom) .
  ln -s $(build-classpath junit) .
  ln -s $(build-classpath log4j) .
  ln -s $(build-classpath objectweb-asm/asm-all) .
  ln -s $(build-classpath oro) .
  ln -s $(build-classpath xalan-j2) .
  ln -s $(build-classpath tomcat-servlet-3.0-api) servlet-api.jar
  ln -s $(build-classpath apache-commons-cli) commons-cli.jar
  pushd xerces
    ln -s $(build-classpath xalan-j2) .
    ln -s $(build-classpath xml-commons-apis) .
  popd
popd

pushd antLibrary/common
  ln -s $(build-classpath groovy) .
popd

export CLASSPATH=$(build-classpath objectweb-asm/asm-all commons-cli antlr-tool junit)
%ant -Djetty.dir=. -Dlib.dir=. compile jar javadoc
%{?scl:EOF}

%install
%{?scl:scl enable maven30 %{scl} - <<"EOF_SCL"}
set -e -x
# jars
install -d -m 755 %{buildroot}%{_javadir}
install -p -m 644 %{pkg_name}.jar %{buildroot}%{_javadir}/%{pkg_name}.jar
(cd %{buildroot}%{_javadir} && ln -s %{pkg_name}.jar %{pkg_name}-runtime.jar)

# pom
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_mavenpomdir}/JPP-%{pkg_name}.pom
install -p -m 644 %{SOURCE2} %{buildroot}%{_mavenpomdir}/JPP-%{pkg_name}-runtime.pom

# depmap
%add_maven_depmap JPP-%{pkg_name}.pom %{pkg_name}.jar -a "%{pkg_name}:%{pkg_name}"
%add_maven_depmap JPP-%{pkg_name}-runtime.pom %{pkg_name}-runtime.jar -a "%{pkg_name}:%{pkg_name}-runtime"

# ant config
install -d -m 755  %{buildroot}%{_sysconfdir_java_common}/ant.d
cat > %{buildroot}%{_sysconfdir_java_common}/ant.d/%{pkg_name} << EOF
ant cobertura junit4 log4j oro xerces-j2
EOF

# javadoc
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -rp build/api/* %{buildroot}%{_javadocdir}/%{name}
%{?scl:EOF_SCL}

%files -f .mfiles
%doc ChangeLog COPYING COPYRIGHT README LICENSE-ASL-1.1 LICENSE-ASL-2.0
%config %{_sysconfdir_java_common}/ant.d/%{pkg_name}

%files javadoc
%doc COPYING COPYRIGHT LICENSE-ASL-1.1 LICENSE-ASL-2.0
%{_javadocdir}/%{name}

%changelog
* Sat Jan 09 2016 Michal Srb <msrb@redhat.com> - 1.9.4.1-9.14
- maven33 rebuild

* Thu Jan 15 2015 Michael Simacek <msimacek@redhat.com> - 1.9.4.1-9.13
- Install ant.d files into rh-java-common's ant.d

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1.9.4.1-9.12
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michael Simacek <msimacek@redhat.com> - 1.9.4.1-9.11
- BR/R on packages from rh-java-common

* Wed Jan 07 2015 Michal Srb <msrb@redhat.com> - 1.9.4.1-9.10
- Migrate to .mfiles

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 1.9.4.1-9.9
- Mass rebuild 2015-01-06

* Mon Jun  2 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.8
- Skip running tests

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.7
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.6
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.5
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.4
- Remove requires on java

* Fri Feb 14 2014 Michael Simacek <msimacek@redhat.com> - 1.9.4.1-9.3
- SCL-ize BRs

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-9.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.9.4.1-9
- Mass rebuild 2013-12-27

* Fri Aug 02 2013 Michal Srb <msrb@redhat.com> - 1.9.4.1-8
- Add create-tarball.sh script to SRPM

* Mon Jul 22 2013 Michal Srb <msrb@redhat.com> - 1.9.4.1-7
- Fix license tag
- Add ASL 2.0 license text
- Remove unneeded files licensed under questionable license

* Fri Jul 19 2013 Michal Srb <msrb@redhat.com> - 1.9.4.1-6
- Provide URL for Source1 and Source2

* Wed Jul 17 2013 Michal Srb <msrb@redhat.com> - 1.9.4.1-5
- Build from clean tarball

* Wed Jul 03 2013 Michal Srb <msrb@redhat.com> - 1.9.4.1-4
- Replace servlet 2.5 with servlet 3.0 (Resolves: #979499)
- Install ASL 1.1 license file
- Spec file clean up

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.9.4.1-4
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov 27 2012 Tomas Radej <tradej@redhat.com> - 1.9.4.1-2
- Added MPL to licence field

* Sun Oct 14 2012 Mat Booth <fedora@matbooth.co.uk> - 1.9.4.1-1
- Update for latest guidelines.
- Update to latest upstream version, bug 848871.
- Fix directory ownership, bug 850004.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Apr 12 2012 Tomas Radej <tradej@redhat.com> - 1.9.3-5
- Fixed unmappable characters

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec 13 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.9.3-2
- Fix objectweb-asm groupId in pom files
- Use simple ln -s and build-classpath to symlink jars
- Versionless jars

* Mon Jun 21 2010 Victor G. Vasilyev <victor.vasilyev@sun.com> 1.9.3-1
- Release 1.9.3

* Wed Aug 19 2009 Victor G. Vasilyev <victor.vasilyev@sun.com> 1.9-3
- Fix B(R) according to guidelines
- Use the  lnSysJAR macro
- Prevent brp-java-repack-jars from being run

* Sun Aug 09 2009 Victor G. Vasilyev <victor.vasilyev@sun.com> 1.9-2
- The license tag is changed according to http://cobertura.sourceforge.net/license.html

* Fri Jun 19 2009 Victor G. Vasilyev <victor.vasilyev@sun.com> 1.9-1
- release 1.9
