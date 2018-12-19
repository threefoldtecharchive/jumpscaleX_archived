import pytest
import unittest
import sys
from unittest import mock
from Jumpscale import j
from unittest.mock import MagicMock
from github.GithubObject import NotSet
class TestGuthubClient(unittest.TestCase):
    
    def tearDown(self):
        """
        TearDown
        """
        # clean up all the imported modules from jumpscale (we know that its not clean and it does not clean up all the refences)
        for module in sorted([item for item in sys.modules.keys() if 'Jumpscale' in item], reverse=True):
            del sys.modules[module]

    @pytest.mark.github_client
    @mock.patch('JumpscaleLib.clients.github.Github.github.Github')
    def test_organizations_get(self, mock_github):
        """
        check if organizations_get working
        """
        githubclient = j.clients.github.get()
        githubclient.organizations_get()
        # assert the expected call for get_orgs
        githubclient.api.get_user().get_orgs.assert_called_with()

    @pytest.mark.github_client
    @mock.patch('JumpscaleLib.clients.github.Github.github.Github')
    def test_repos_get(self, mock_github):
        """
        check if repos_get working
        """
        githubclient = j.clients.github.get()
        # test repo_get without organization_id
        githubclient.repos_get()
        # assert the expected call for get_user().get_repos if no organization id provided
        githubclient.api.get_user().get_repos.assert_called_with()

        # test repo_get with organization_id
        try:
            githubclient.repos_get(organization_id="id")
            assert False, "failed to raise runtime error when no organizations found"
        except RuntimeError:    
            # assert the expected call for get_user().get_orgs if organization id provided
            githubclient.api.get_user().get_orgs.assert_called_with()

    @pytest.mark.github_client
    @mock.patch('JumpscaleLib.clients.github.Github.github.Github')
    def test_repo_get(self, mock_github):
        """
        check if repo_get working
        """
        githubclient = j.clients.github.get()
        githubclient.repo_get("repo")
        # assert the expected call for get_repo
        githubclient.api.get_user().get_repo.assert_called_with("repo")

    @pytest.mark.github_client
    @mock.patch('JumpscaleLib.clients.github.Github.github.Github')
    def test_repo_create(self, mock_github):
        """
        check if repo_create working
        """
        githubclient = j.clients.github.get()
        githubclient.repo_create("repo")
        # assert the expected call for create_repo
        githubclient.api.get_user().create_repo.assert_called_with("repo", description=NotSet, homepage=NotSet, private=NotSet, has_issues=NotSet, has_wiki=NotSet,
                    has_downloads=NotSet, auto_init=NotSet, gitignore_template=NotSet)
    
    @pytest.mark.github_client
    @mock.patch('JumpscaleLib.clients.github.Github.github.Github')
    @mock.patch('JumpscaleLib.clients.github.Github.github.Repository')
    def test_repo_delete(self, mock_github, mock_repository):
        """
        check if repo_delete working
        """
        githubclient = j.clients.github.get()
        repo = mock_repository
        githubclient.repo_delete(repo)
        # assert the expected call for delete
        mock_repository.delete.assert_called_with()
    
