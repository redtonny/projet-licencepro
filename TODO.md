# TODO.md - Améliorations Modernes Parc Informatique EPCCI

## Plan Approuvé
✅ Plan confirmé par l'utilisateur.

## Étapes à compléter (dans l'ordre) :

### Étape 1: Setup Dépendances & Base.html (HTMX/Alpine/Flowbite)
- [x] Installer deps via execute_command
- [x] Edit base.html : Ajouter CDNs HTMX/Alpine.js/Flowbite + dark toggle + toasts
- [x] Test base.html reload

### Étape 2: Refacto Vues Ticket → CBV
- [x] Edit ticket/views.py : ListView/CreateView/UpdateView
- [x] Edit ticket/urls.py si besoin
- [x] Edit templates/ticket/liste.html HTMX + Flowbite table + modals

### Étape 3: HTMX sur Tickets (CRUD sans reload)
- [x] Edit templates/ticket/liste.html : HTMX table + inline create + pagination
- [x] Edit templates/ticket/creation.html : HTMX form modern dark/grid
- [x] Edit templates/ticket/assigner_ticket.html : HTMX form modern
- [x] Test tickets flow (runserver)

### Étape 4: django-tables2 pour toutes listes
- [ ] pip install django-tables2
- [ ] Create tables.py dans chaque app
- [ ] Edit views/templates pour TableView

### Étape 5: Dashboard Charts
- [ ] pip install django-chartjs
- [ ] Edit dashboard view/template : graphs tickets/interventions

### Étape 6: DRF API + Tests
- [ ] DRF setup
- [ ] API endpoints
- [ ] pytest basics

**Prochaines actions :** Marquer comme fait au fur/à mesure.

*Généré par BLACKBOXAI*
