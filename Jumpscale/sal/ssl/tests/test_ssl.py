import subprocess 
from Jumpscale import j
from Jumpscale.sal.ssl.SSLFactory import SSLFactory

SSLFactory = SSLFactory()

def test_ca_generate():
    
    """
    to run
    js.shell 'j.sal.ssl.ca_cert_generate(cert_dir='/test')'
    CA (Certificate Authority) generate
    """
    
    SSLFactory.ca_cert_generate('/tmp/test/')
    file_list = subprocess.run('ls -la /tmp/test/', shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE) 
    files = file_list.stdout.decode()
    assert ca.key in files
    assert ca.crt in files

def test_verify():

    """
        to run
        js.shell 'j.sal.ssl.verify('/tmp/test/ca.crt', '/tmp/test/ca.key')
    """

    output = SSLFactory.verify('/tmp/test/ca.crt', '/tmp/test/ca.key')
    assert output is True

def test_certificate_signing_request_create():

    """
       to run 
       js.shell 'j.sal.ssl.certificate_signing_request_create('test')'

    """

    output = SSLFactory.certificate_signing_request_create('test')
    assert "BEGIN PRIVATE KEY" in str(output)
    assert "END PRIVATE KEY" in str(output)
    assert "BEGIN CERTIFICATE REQUEST" in str(output)
    assert "END CERTIFICATE REQUEST" in str(output)


